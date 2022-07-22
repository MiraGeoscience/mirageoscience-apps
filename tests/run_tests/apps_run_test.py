#  Copyright (c) 2022 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).
import uuid
from os import listdir, path

from geoh5py.objects import Curve
from geoh5py.workspace import Workspace

from geoapps.block_model_creation.application import BlockModelCreation
from geoapps.calculator import Calculator
from geoapps.clustering.application import Clustering
from geoapps.contours.application import ContourValues
from geoapps.coordinate_transformation import CoordinateTransformation
from geoapps.edge_detection.application import EdgeDetectionApp
from geoapps.export.application import Export
from geoapps.interpolation import DataInterpolation
from geoapps.iso_surfaces.application import IsoSurface
from geoapps.triangulated_surfaces.application import Surface2D
from geoapps.utils.testing import get_output_workspace

# import pytest
# pytest.skip("eliminating conflicting test.", allow_module_level=True)

PROJECT = "./FlinFlon.geoh5"
GEOH5 = Workspace(PROJECT)


def test_block_model(tmp_path):
    temp_workspace = path.join(tmp_path, "contour.geoh5")
    with Workspace(temp_workspace) as workspace:
        for uid in ["{2e814779-c35f-4da0-ad6a-39a6912361f9}"]:
            GEOH5.get_entity(uuid.UUID(uid))[0].copy(parent=workspace)

    app = BlockModelCreation(geoh5=temp_workspace, output_path=str(tmp_path))
    app.trigger_click(None)

    filename = list(
        filter(lambda x: ("BlockModel_" in x) and ("geoh5" in x), listdir(tmp_path))
    )[0]
    with Workspace(path.join(tmp_path, filename)) as workspace:
        ent = workspace.get_entity("BlockModel")
        assert (len(ent) == 1) and (ent[0] is not None)


def test_calculator(tmp_path):
    temp_workspace = path.join(tmp_path, "contour.geoh5")
    with Workspace(temp_workspace) as workspace:
        GEOH5.get_entity("geochem")[0].copy(parent=workspace)

    app = Calculator(h5file=temp_workspace)
    app.trigger.click()

    with Workspace(get_output_workspace(tmp_path)) as workspace:
        output = workspace.get_entity("NewChannel")[0]
        assert output.values.shape[0] == 4438, "Change in output. Need to verify."


def test_coordinate_transformation(tmp_path):
    temp_workspace = path.join(tmp_path, "contour.geoh5")
    with Workspace(temp_workspace) as workspace:
        GEOH5.get_entity("Gravity_Magnetics_drape60m")[0].copy(parent=workspace)
        GEOH5.get_entity("Data_TEM_pseudo3D")[0].copy(parent=workspace)

    app = CoordinateTransformation(h5file=temp_workspace)
    app.trigger.click()

    with Workspace(get_output_workspace(tmp_path)) as workspace:
        assert len(workspace.objects) == 2, "Coordinate transform failed."


def test_contour_values(tmp_path):
    temp_workspace = path.join(tmp_path, "contour.geoh5")
    with Workspace(temp_workspace) as workspace:
        GEOH5.get_entity(uuid.UUID("{538a7eb1-2218-4bec-98cc-0a759aa0ef4f}"))[0].copy(
            parent=workspace
        )

    app = ContourValues(geoh5=temp_workspace, plot_result=False)
    app.trigger.click()

    with Workspace(get_output_workspace(tmp_path)) as workspace:
        output = workspace.get_entity("contours")[0]
        assert output.n_vertices == 3000, "Change in output. Need to verify."


def test_create_surface(tmp_path):
    temp_workspace = path.join(tmp_path, "contour.geoh5")
    with Workspace(temp_workspace) as workspace:
        for uid in [
            "{5fa66412-3a4c-440c-8b87-6f10cb5f1c7f}",
        ]:
            GEOH5.get_entity(uuid.UUID(uid))[0].copy(parent=workspace)

    app = Surface2D(h5file=temp_workspace)
    app.trigger.click()

    with Workspace(get_output_workspace(tmp_path)) as workspace:
        group = workspace.get_entity("CDI")[0]
        assert len(group.children) == 1


def test_clustering(tmp_path):
    temp_workspace = path.join(tmp_path, "contour.geoh5")
    with Workspace(temp_workspace) as workspace:
        for uid in ["{79b719bc-d996-4f52-9af0-10aa9c7bb941}"]:
            GEOH5.get_entity(uuid.UUID(uid))[0].copy(parent=workspace)

    app = Clustering(geoh5=temp_workspace, output_path=str(tmp_path))
    app.trigger_click(None)

    filename = list(
        filter(lambda x: ("Clustering_" in x) and ("geoh5" in x), listdir(tmp_path))
    )[0]
    with Workspace(path.join(tmp_path, filename)) as workspace:
        assert len(workspace.get_entity("Clusters")) == 1


def test_data_interpolation(tmp_path):
    temp_workspace = path.join(tmp_path, "contour.geoh5")
    with Workspace(temp_workspace) as workspace:
        for uid in [
            "{2e814779-c35f-4da0-ad6a-39a6912361f9}",
            "{f3e36334-be0a-4210-b13e-06933279de25}",
            "{7450be38-1327-4336-a9e4-5cff587b6715}",
            "{ab3c2083-6ea8-4d31-9230-7aad3ec09525}",
        ]:
            GEOH5.get_entity(uuid.UUID(uid))[0].copy(parent=workspace)

    app = DataInterpolation(h5file=temp_workspace)
    app.trigger.click()

    with Workspace(get_output_workspace(tmp_path)) as workspace:
        assert len(workspace.get_entity("Iteration_7_model_Interp")) == 1


def test_edge_detection(tmp_path):
    temp_workspace = path.join(tmp_path, "contour.geoh5")
    with Workspace(temp_workspace) as workspace:
        for uid in [
            "{538a7eb1-2218-4bec-98cc-0a759aa0ef4f}",
        ]:
            GEOH5.get_entity(uuid.UUID(uid))[0].copy(parent=workspace)

    app = EdgeDetectionApp(geoh5=temp_workspace, plot_result=False)

    app.trigger_click(None)

    with Workspace(get_output_workspace(tmp_path)) as workspace:
        assert (
            len(
                [
                    child
                    for child in workspace.get_entity("Airborne_Gxx")
                    if isinstance(child, Curve)
                ]
            )
            == 1
        )


def test_export():
    app = Export(h5file=PROJECT)
    app.trigger.click()


def test_iso_surface(tmp_path):
    temp_workspace = path.join(tmp_path, "contour.geoh5")
    with Workspace(temp_workspace) as workspace:
        for uid in [
            "{2e814779-c35f-4da0-ad6a-39a6912361f9}",
        ]:
            GEOH5.get_entity(uuid.UUID(uid))[0].copy(parent=workspace)

    app = IsoSurface(geoh5=temp_workspace)
    app.trigger.click()

    with Workspace(get_output_workspace(tmp_path)) as workspace:
        group = workspace.get_entity("Isosurface")[0]
        assert len(group.children) == 5
