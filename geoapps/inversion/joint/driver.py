#  Copyright (c) 2023 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

# pylint: disable=unexpected-keyword-arg, no-value-for-parameter

from __future__ import annotations

import sys
from warnings import warn

import numpy as np
from geoh5py.ui_json import InputFile
from SimPEG.objective_function import ComboObjectiveFunction

from geoapps.driver_base.utils import treemesh_2_octree
from geoapps.inversion import DRIVER_MAP
from geoapps.inversion.components import InversionMesh
from geoapps.inversion.components.factories import SaveIterationGeoh5Factory
from geoapps.inversion.driver import InversionDriver
from geoapps.inversion.joint.params import BaseJointParams
from geoapps.utils.models import create_octree_from_octrees, get_octree_attributes


class BaseJointDriver(InversionDriver):
    _drivers = None

    def __init__(self, params: BaseJointParams):
        super().__init__(params)

    @property
    def data_misfit(self):
        if getattr(self, "_data_misfit", None) is None and self.drivers is not None:
            objective_functions = []

            for driver in self.drivers:
                if driver.data_misfit is not None:
                    objective_functions += driver.data_misfit.objfcts

            self._data_misfit = ComboObjectiveFunction(objective_functions)

        return self._data_misfit

    @property
    def drivers(self) -> list[InversionDriver] | None:
        """List of inversion drivers."""
        if self._drivers is None:
            drivers = []
            physical_property = []
            # Create sub-drivers
            for group in [
                self.params.group_a,
                self.params.group_b,
                self.params.group_c,
            ]:
                if group is None:
                    continue

                ui_json = group.options
                ui_json["geoh5"] = self.workspace

                ifile = InputFile(ui_json=ui_json)
                mod_name, class_name = DRIVER_MAP.get(ifile.data["inversion_type"])
                module = __import__(mod_name, fromlist=[class_name])
                inversion_driver = getattr(module, class_name)
                params = inversion_driver._params_class(  # pylint: disable=W0212
                    ifile, out_group=group
                )
                driver = inversion_driver(params)
                physical_property.append(params.physical_property)
                group.parent = self.params.out_group
                drivers.append(driver)

            self.params.physical_property = physical_property
            self._drivers = drivers

        return self._drivers

    def get_local_actives(self, driver: InversionDriver):
        """Get all local active cells within the global mesh for a given driver."""

        in_local = driver.inversion_mesh.mesh._get_containing_cell_indexes(  # pylint: disable=W0212
            self.inversion_mesh.mesh.gridCC
        )
        local_actives = driver.inversion_topography.active_cells(
            driver.inversion_mesh, driver.inversion_data
        )
        global_active = local_actives[in_local]
        global_active[
            ~driver.inversion_mesh.mesh.isInside(self.inversion_mesh.mesh.gridCC)
        ] = False
        return global_active

    def initialize(self):
        """Generate sub drivers."""
        raise NotImplementedError("Must be implemented by subclass.")

    @property
    def inversion_data(self):
        """Inversion data"""
        return self._inversion_data

    @property
    def inversion_mesh(self):
        """Inversion mesh"""
        if getattr(self, "_inversion_mesh", None) is None:
            self._inversion_mesh = InversionMesh(
                self.workspace,
                self.params,
                self.inversion_data,
                self.inversion_topography,
            )
        return self._inversion_mesh

    def validate_create_mesh(self):
        """Function to validate and create the inversion mesh."""

        if self.params.mesh is None:
            print("Creating a global mesh from sub-meshes parameters.")
            tree = create_octree_from_octrees(
                [driver.inversion_mesh.mesh for driver in self.drivers]
            )
            self.params.mesh = treemesh_2_octree(self.workspace, tree)

        cell_size = []
        for driver in self.drivers:
            attributes = get_octree_attributes(driver.params.mesh)

            if cell_size and not cell_size == attributes["cell_size"]:
                raise ValueError(
                    f"Cell size mismatch in dimension {cell_size} != {attributes['cell_size']}"
                )
            else:
                cell_size = attributes["cell_size"]

            local_mesh = driver.inversion_mesh.mesh
            origin = local_mesh.origin
            base_level = (
                local_mesh.max_level
                - 1
                - np.min(
                    local_mesh._cell_levels_by_indexes(  # pylint: disable=W0212
                        np.arange(local_mesh.nC)
                    )
                )
            )
            shift = np.zeros(3)
            for dim in range(self.inversion_mesh.mesh.dim):
                base_size = self.inversion_mesh.mesh.h[dim][0] * 2**base_level
                nodal = self.inversion_mesh.mesh.origin[dim] + np.cumsum(
                    np.r_[
                        0,
                        np.ones(int(np.log2(len(self.inversion_mesh.mesh.h[dim]))))
                        * base_size,
                    ]
                )
                closest = np.argmin(np.abs(nodal - origin[dim]))
                shift[dim] = nodal[closest] - origin[dim]

            if np.any(shift != 0.0):
                warn(
                    f"Shifting {driver} mesh origin by {shift} m to match inversion mesh."
                )
                driver.inversion_mesh.entity.origin = np.r_[
                    driver.inversion_mesh.entity.origin["x"] - shift[0],
                    driver.inversion_mesh.entity.origin["y"] - shift[1],
                    driver.inversion_mesh.entity.origin["z"] - shift[2],
                ]
                setattr(driver.inversion_mesh, "_mesh", None)

    def run(self):
        """Run inversion from params"""
        sys.stdout = self.logger
        self.logger.start()
        self.configure_dask()

        if self.params.forward_only:
            print("Running the forward simulation ...")
            predicted = self.inverse_problem.get_dpred(
                self.models.starting, compute_J=False
            )

            for sub, driver in zip(predicted, self.drivers):
                SaveIterationGeoh5Factory(driver.params).build(
                    inversion_object=driver.inversion_data,
                    sorting=np.argsort(np.hstack(driver.sorting)),
                    ordering=driver.ordering,
                ).save_components(0, sub)
        else:
            # Run the inversion
            self.start_inversion_message()
            self.inversion.run(self.models.starting)

        self.logger.end()
        sys.stdout = self.logger.terminal
        self.logger.log.close()