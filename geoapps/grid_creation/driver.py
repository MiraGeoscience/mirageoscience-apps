#  Copyright (c) 2022 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).
from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree

from geoapps.grid_creation.params import GridCreationParams
from geoapps.interpolation.application import DataInterpolation
from geoapps.shared_utils.utils import get_locations


class GridCreationDriver:
    def __init__(self, params: GridCreationParams):
        self.params: GridCreationParams = params

    def run(self):
        print(self.params.to_dict().items())

        xyz = get_locations(self.params.geoh5, self.params.objects)
        if xyz is None:
            return

        tree = cKDTree(xyz)

        xyz_ref = get_locations(self.params.geoh5, self.params.xy_reference)
        if xyz_ref is None:
            print("No object selected for 'Lateral Extent'. Defaults to input object.")
            xyz_ref = xyz

        # Find extent of grid
        h = np.asarray(self.params.core_cell_size.split(",")).astype(float).tolist()

        pads = (
            np.asarray(self.params.padding_distance.split(",")).astype(float).tolist()
        )

        object_out = DataInterpolation.get_block_model(
            self.params.geoh5,
            self.params.new_grid,
            xyz_ref,
            h,
            self.params.depth_core,
            pads,
            self.params.expansion_fact,
        )

        # Try to recenter on nearest
        # Find nearest cells
        rad, ind = tree.query(object_out.centroids)
        ind_nn = np.argmin(rad)

        d_xyz = object_out.centroids[ind_nn, :] - xyz[ind[ind_nn], :]

        object_out.origin = np.r_[object_out.origin.tolist()] - d_xyz

        # xyz_out = object_out.centroids.copy()
