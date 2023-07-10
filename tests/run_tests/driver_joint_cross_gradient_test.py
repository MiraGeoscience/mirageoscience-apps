#  Copyright (c) 2023 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).
from pathlib import Path

import numpy as np
from geoh5py.groups import SimPEGGroup
from geoh5py.objects import Octree
from geoh5py.workspace import Workspace

from geoapps.inversion.joint.joint_cross_gradient import JointCrossGradientParams
from geoapps.inversion.joint.joint_cross_gradient.driver import JointCrossGradientDriver
from geoapps.inversion.potential_fields import (
    GravityParams,
    MagneticScalarParams,
    MagneticVectorParams,
)
from geoapps.inversion.potential_fields.gravity.driver import GravityDriver
from geoapps.inversion.potential_fields.magnetic_scalar.driver import (
    MagneticScalarDriver,
)
from geoapps.inversion.potential_fields.magnetic_vector.driver import (
    MagneticVectorDriver,
)
from geoapps.shared_utils.utils import get_inversion_output
from geoapps.utils.testing import check_target, setup_inversion_workspace

# To test the full run and validate the inversion.
# Move this file out of the test directory and run.

target_run = {
    "data_norm": 0.104056,
    "phi_d": 427,
    "phi_m": 6.558,
}


def test_joint_cross_gradient_fwr_run(
    tmp_path,
    n_grid_points=4,
    refinement=(2,),
):
    np.random.seed(0)
    # Create local problem A
    geoh5, _, model, survey, topography = setup_inversion_workspace(
        tmp_path,
        background=0.0,
        anomaly=0.75,
        refinement=refinement,
        n_electrodes=n_grid_points,
        n_lines=n_grid_points,
    )
    params = GravityParams(
        forward_only=True,
        geoh5=geoh5,
        mesh=model.parent.uid,
        topography_object=topography.uid,
        resolution=0.0,
        z_from_topo=False,
        data_object=survey.uid,
        starting_model=model.uid,
    )
    fwr_driver_a = GravityDriver(params)

    _, _, model, survey, _ = setup_inversion_workspace(
        tmp_path,
        background=0.0,
        anomaly=0.05,
        refinement=refinement,
        n_electrodes=n_grid_points,
        n_lines=n_grid_points,
        flatten=False,
    )
    inducing_field = (50000.0, 90.0, 0.0)
    params = MagneticScalarParams(
        forward_only=True,
        geoh5=geoh5,
        mesh=model.parent.uid,
        topography_object=topography.uid,
        inducing_field_strength=inducing_field[0],
        inducing_field_inclination=inducing_field[1],
        inducing_field_declination=inducing_field[2],
        resolution=0.0,
        z_from_topo=False,
        data_object=survey.uid,
        starting_model=model.uid,
    )
    params.workpath = tmp_path
    fwr_driver_b = MagneticScalarDriver(params)

    # Force co-location of meshes
    fwr_driver_b.inversion_mesh.entity.origin = (
        fwr_driver_a.inversion_mesh.entity.origin
    )
    fwr_driver_b.workspace.update_attribute(
        fwr_driver_b.inversion_mesh.entity, "attributes"
    )
    fwr_driver_b.inversion_mesh._mesh = None  # pylint: disable=protected-access

    fwr_driver_a.run()
    fwr_driver_b.run()
    geoh5.close()
    return np.r_[fwr_driver_a.models.starting, fwr_driver_b.models.starting]


def test_joint_cross_gradient_inv_run(
    tmp_path,
    max_iterations=1,
    pytest=True,
):
    workpath = tmp_path / "inversion_test.ui.geoh5"
    if pytest:
        workpath = (
            tmp_path.parent
            / "test_joint_cross_gradient_fwr_0"
            / "inversion_test.ui.geoh5"
        )

    with Workspace(workpath) as geoh5:
        topography = geoh5.get_entity("topography")[0]
        drivers = []
        orig_data = []

        for group in geoh5.groups:
            if not isinstance(group, SimPEGGroup):
                continue

            for child in group.children:
                if isinstance(child, Octree):
                    mesh = child
                else:
                    survey = child

            data = survey.children[0]
            orig_data.append(data.values)

            if group.options["inversion_type"] == "gravity":
                params = GravityParams(
                    geoh5=geoh5,
                    mesh=mesh.uid,
                    topography_object=topography.uid,
                    data_object=survey.uid,
                    gz_channel=data.uid,
                    gz_uncertainty=1e-3,
                    starting_model=0.0,
                )
                drivers.append(GravityDriver(params))
            else:
                params = MagneticVectorParams(
                    geoh5=geoh5,
                    mesh=mesh.uid,
                    topography_object=topography.uid,
                    inducing_field_strength=group.options["inducing_field_strength"][
                        "value"
                    ],
                    inducing_field_inclination=group.options[
                        "inducing_field_inclination"
                    ]["value"],
                    inducing_field_declination=group.options[
                        "inducing_field_declination"
                    ]["value"],
                    data_object=survey.uid,
                    starting_model=1e-4,
                    reference_model=0.0,
                    lower_bound=0.0,
                    tmi_channel=data.uid,
                    tmi_uncertainty=1.0,
                )
                drivers.append(MagneticVectorDriver(params))

        # Run the inverse
        np.random.seed(0)
        joint_params = JointCrossGradientParams(
            geoh5=geoh5,
            topography_object=topography.uid,
            group_a=drivers[0].params.out_group,
            group_b=drivers[1].params.out_group,
            max_global_iterations=max_iterations,
            initial_beta_ratio=1e-2,
            prctile=100,
            gradient_type="components",
            store_sensitivities="ram",
        )

    driver = JointCrossGradientDriver(joint_params)
    driver.run()

    with Workspace(driver.params.geoh5.h5file):
        output = get_inversion_output(
            driver.params.geoh5.h5file, driver.params.out_group.uid
        )

        output["data"] = np.hstack(orig_data)
        if pytest:
            check_target(output, target_run)
        else:
            return driver.inverse_problem.model


if __name__ == "__main__":
    # Full run
    m_start = test_joint_cross_gradient_fwr_run(
        Path("./"),
        n_grid_points=20,
        refinement=(4, 8),
    )

    m_rec = test_joint_cross_gradient_inv_run(
        Path("./"),
        max_iterations=15,
        pytest=False,
    )
    model_residual = np.linalg.norm(m_rec - m_start) / np.linalg.norm(m_start) * 100.0
    assert (
        model_residual < 75.0
    ), f"Deviation from the true solution is {model_residual:.2f}%. Validate the solution!"
    print("Recovered model is within 15% of the answer. Let's go!!")
