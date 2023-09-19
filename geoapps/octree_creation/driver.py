#  Copyright (c) 2023 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).


from __future__ import annotations

import sys

from discretize import TreeMesh
from discretize.utils import mesh_builder_xyz, refine_tree_xyz
from geoh5py.objects import Curve, ObjectBase, Octree
from geoh5py.shared.utils import fetch_active_workspace
from geoh5py.ui_json import utils

from geoapps.driver_base.driver import BaseDriver
from geoapps.driver_base.utils import treemesh_2_octree
from geoapps.octree_creation.constants import validations
from geoapps.octree_creation.params import OctreeParams
from geoapps.shared_utils.utils import densify_curve


class OctreeDriver(BaseDriver):
    _params_class = OctreeParams
    _validations = validations

    def __init__(self, params: OctreeParams):
        super().__init__(params)
        self.params: OctreeParams = params

    def run(self) -> Octree:
        """
        Create an octree mesh from input values
        """
        with fetch_active_workspace(self.params.geoh5, mode="r+"):
            octree = self.octree_from_params(self.params)
            self.update_monitoring_directory(octree)

        return octree

    @staticmethod
    def minimum_level(treemesh: TreeMesh, level: int):
        """Computes the minimum level of refinement for a given tree mesh."""
        return max([1, treemesh.max_level - level + 1])

    @staticmethod
    def octree_from_params(params: OctreeParams):
        print("Setting the mesh extent")
        entity = params.objects
        treemesh = mesh_builder_xyz(
            entity.vertices,
            [
                params.u_cell_size,
                params.v_cell_size,
                params.w_cell_size,
            ],
            padding_distance=params.get_padding(),
            mesh_type="tree",
            depth_core=params.depth_core,
        )
        minimum_level = OctreeDriver.minimum_level(treemesh, params.minimum_level)
        treemesh.refine(minimum_level, finalize=False)

        for label, value in params.free_parameter_dict.items():
            refinement_object = getattr(params, value["object"])
            levels = utils.str2list(getattr(params, value["levels"]))
            if not isinstance(refinement_object, ObjectBase):
                continue

            print(f"Applying {label} on: {getattr(params, value['object']).name}")

            if isinstance(refinement_object, Curve):
                treemesh = OctreeDriver.refine_tree_from_curve(
                    treemesh, refinement_object, levels
                )

            else:
                # TODO: Add refinement type 'ball' and 'surfacve' as static method
                treemesh = refine_tree_xyz(
                    treemesh,
                    refinement_object.vertices,
                    method=getattr(params, value["type"]),
                    octree_levels=levels,
                    max_distance=getattr(params, value["distance"]),
                    finalize=False,
                )

        print("Finalizing . . .")
        treemesh.finalize()

        octree = treemesh_2_octree(params.geoh5, treemesh, name=params.ga_group_name)

        return octree

    @staticmethod
    def refine_tree_from_curve(
        treemesh: TreeMesh, curve: Curve, levels: list[int], finalize=False
    ) -> TreeMesh:
        """
        Refine a tree mesh along the segments of a curve.

        :param treemesh: Tree mesh to refine.
        :param curve: Curve object to use for refinement.
        :param levels: Number of cells requested at each refinement level.
            Defined in reversed order from highest octree to lowest.
        """
        locs = densify_curve(curve, treemesh.h[0][0])
        distance = 0

        for ii, n_cells in enumerate(levels):
            distance += n_cells * treemesh.h[0][0] * 2**ii

            treemesh.refine_ball(
                locs, distance, treemesh.max_level - ii, finalize=finalize
            )

        return treemesh


if __name__ == "__main__":
    file = sys.argv[1]
    OctreeDriver.start(file)
