#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).


from __future__ import annotations

from pathlib import Path

import numpy as np
from geoh5py.objects import Points
from geoh5py.workspace import Workspace

from geoapps.inversion.components import (
    InversionMesh,
    InversionModel,
    InversionModelCollection,
)
from geoapps.inversion.potential_fields import MagneticVectorParams
from geoapps.inversion.potential_fields.magnetic_vector.driver import (
    MagneticVectorDriver,
)
from geoapps.shared_utils.utils import rotate_xyz
from geoapps.utils.testing import Geoh5Tester

from . import PROJECT

geoh5 = Workspace(PROJECT)


def setup_params(path):
    geotest = Geoh5Tester(geoh5, path, "test.geoh5", MagneticVectorParams)
    geotest.set_param("data_object", "{538a7eb1-2218-4bec-98cc-0a759aa0ef4f}")
    geotest.set_param("tmi_channel", "{44822654-b6ae-45b0-8886-2d845f80f422}")
    geotest.set_param("mesh", "{a8f3b369-10bd-4ca8-8bd6-2d2595bddbdf}")
    geotest.set_param("topography_object", "{ab3c2083-6ea8-4d31-9230-7aad3ec09525}")
    geotest.set_param("topography", "{a603a762-f6cb-4b21-afda-3160e725bf7d}")
    geotest.set_param("starting_model", 1e-04)
    geotest.set_param("inducing_field_inclination", 79.0)
    geotest.set_param("inducing_field_declination", 11.0)
    geotest.set_param("reference_model", 0.0)
    geotest.set_param("reference_inclination", 79.0)
    geotest.set_param("reference_declination", 11.0)

    return geotest.make()


def test_zero_reference_model(tmp_path: Path):
    ws, params = setup_params(tmp_path)
    driver = MagneticVectorDriver(params)
    _ = InversionModel(driver, "reference")
    incl = np.unique(ws.get_entity("reference_inclination")[0].values)
    decl = np.unique(ws.get_entity("reference_declination")[0].values)
    assert len(incl) == 1
    assert len(decl) == 1
    assert np.isclose(incl[0], 79.0)
    assert np.isclose(decl[0], 11.0)


def test_collection(tmp_path: Path):
    _, params = setup_params(tmp_path)
    driver = MagneticVectorDriver(params)
    models = InversionModelCollection(driver)
    models.remove_air(driver.models.active_cells)
    starting = InversionModel(driver, "starting")
    starting.remove_air(driver.models.active_cells)
    np.testing.assert_allclose(models.starting, starting.model, atol=1e-7)


def test_initialize(tmp_path: Path):
    _, params = setup_params(tmp_path)
    driver = MagneticVectorDriver(params)
    starting_model = InversionModel(driver, "starting")
    assert len(starting_model.model) == 3 * driver.inversion_mesh.n_cells
    assert len(np.unique(starting_model.model)) == 3


def test_model_from_object(tmp_path: Path):
    # Test behaviour when loading model from Points object with non-matching mesh
    ws, params = setup_params(tmp_path)
    driver = MagneticVectorDriver(params)

    inversion_mesh = InversionMesh(
        ws, params, driver.inversion_data, driver.inversion_topography
    )
    cc = inversion_mesh.mesh.cell_centers
    m0 = np.array([2.0, 3.0, 1.0])
    vals = (m0[0] * cc[:, 0]) + (m0[1] * cc[:, 1]) + (m0[2] * cc[:, 2])

    point_object = Points.create(ws, name="test_point", vertices=cc)
    point_object.add_data({"test_data": {"values": vals}})
    data_object = ws.get_entity("test_data")[0]
    params.lower_bound = data_object.uid
    lower_bound = InversionModel(driver, "lower_bound")
    nc = int(len(lower_bound.model) / 3)
    A = driver.inversion_mesh.mesh.cell_centers
    b = lower_bound.model[:nc]
    from scipy.linalg import lstsq

    m = lstsq(A, b)[0]
    np.testing.assert_array_almost_equal(m, m0, decimal=1)


def test_permute_2_octree(tmp_path: Path):
    ws, params = setup_params(tmp_path)
    driver = MagneticVectorDriver(params)
    params.lower_bound = 0.0
    inversion_mesh = InversionMesh(
        ws, params, driver.inversion_data, driver.inversion_topography
    )
    lower_bound = InversionModel(driver, "lower_bound")
    cc = inversion_mesh.mesh.cell_centers
    center = np.mean(cc, axis=0)
    dx = inversion_mesh.mesh.h[0].min()
    dy = inversion_mesh.mesh.h[1].min()
    dz = inversion_mesh.mesh.h[2].min()
    xmin = center[0] - (5 * dx)
    xmax = center[0] + (5 * dx)
    ymin = center[1] - (5 * dy)
    ymax = center[1] + (5 * dy)
    zmin = center[2] - (5 * dz)
    zmax = center[2] + (5 * dz)
    xind = (cc[:, 0] > xmin) & (cc[:, 0] < xmax)
    yind = (cc[:, 1] > ymin) & (cc[:, 1] < ymax)
    zind = (cc[:, 2] > zmin) & (cc[:, 2] < zmax)
    ind = xind & yind & zind
    lower_bound.model[np.tile(ind, 3)] = 1
    lb_perm = lower_bound.permute_2_octree()

    locs_perm = params.mesh.centroids[lb_perm[: params.mesh.n_cells] == 1, :]
    origin = [float(params.mesh.origin[k]) for k in ["x", "y", "z"]]
    locs_perm_rot = rotate_xyz(locs_perm, origin, -params.mesh.rotation)
    assert xmin <= locs_perm_rot[:, 0].min()
    assert xmax >= locs_perm_rot[:, 0].max()
    assert ymin <= locs_perm_rot[:, 1].min()
    assert ymax >= locs_perm_rot[:, 1].max()
    assert zmin <= locs_perm_rot[:, 2].min()
    assert zmax >= locs_perm_rot[:, 2].max()


def test_permute_2_treemesh(tmp_path: Path):
    ws, params = setup_params(tmp_path)
    driver = MagneticVectorDriver(params)
    cc = params.mesh.centroids
    center = np.mean(cc, axis=0)
    dx = params.mesh.u_cell_size.min()
    dy = params.mesh.v_cell_size.min()
    dz = np.abs(params.mesh.w_cell_size.min())
    xmin = center[0] - (5 * dx)
    xmax = center[0] + (5 * dx)
    ymin = center[1] - (5 * dy)
    ymax = center[1] + (5 * dy)
    zmin = center[2] - (5 * dz)
    zmax = center[2] + (5 * dz)
    xind = (cc[:, 0] > xmin) & (cc[:, 0] < xmax)
    yind = (cc[:, 1] > ymin) & (cc[:, 1] < ymax)
    zind = (cc[:, 2] > zmin) & (cc[:, 2] < zmax)
    ind = xind & yind & zind
    model = np.zeros(params.mesh.n_cells, dtype=float)
    model[ind] = 1
    params.mesh.add_data({"test_model": {"values": model}})
    params.upper_bound = ws.get_entity("test_model")[0].uid
    upper_bound = InversionModel(driver, "upper_bound")
    locs = driver.inversion_mesh.mesh.cell_centers
    locs = locs[upper_bound.model[: driver.inversion_mesh.mesh.nC] == 1, :]
    assert xmin <= locs[:, 0].min()
    assert xmax >= locs[:, 0].max()
    assert ymin <= locs[:, 1].min()
    assert ymax >= locs[:, 1].max()
    assert zmin <= locs[:, 2].min()
    assert zmax >= locs[:, 2].max()
