#  Copyright (c) 2021 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

from uuid import UUID

import numpy as np
from geoh5py.groups import ContainerGroup
from geoh5py.workspace import Workspace

from geoapps.io.Inversion.constants import default_ui_json as base_default_ui_json
from geoapps.io.Inversion.constants import (
    required_parameters as base_required_parameters,
)
from geoapps.io.Inversion.constants import validations as base_validations

################# defaults ##################

inversion_defaults = {
    "title": "SimPEG Gravity Inversion",
    "inversion_type": "gravity",
    "geoh5": None,  # Must remain at top of list for notebook app initialization
    "forward_only": False,
    "topography_object": None,
    "topography": None,
    "data_object": None,
    "gz_channel_bool": False,
    "gz_channel": None,
    "gz_uncertainty": 1.0,
    "guv_channel_bool": False,
    "guv_channel": None,
    "guv_uncertainty": 1.0,
    "gxy_channel_bool": False,
    "gxy_channel": None,
    "gxy_uncertainty": 1.0,
    "gxx_channel_bool": False,
    "gxx_channel": None,
    "gxx_uncertainty": 1.0,
    "gyy_channel_bool": False,
    "gyy_channel": None,
    "gyy_uncertainty": 1.0,
    "gzz_channel_bool": False,
    "gzz_channel": None,
    "gzz_uncertainty": 1.0,
    "gxz_channel_bool": False,
    "gxz_channel": None,
    "gxz_uncertainty": 1.0,
    "gyz_channel_bool": False,
    "gyz_channel": None,
    "gyz_uncertainty": 1.0,
    "gx_channel_bool": False,
    "gx_channel": None,
    "gx_uncertainty": 1.0,
    "gy_channel_bool": False,
    "gy_channel": None,
    "gy_uncertainty": 1.0,
    "starting_model_object": None,
    "starting_model": None,
    "tile_spatial": 1,
    "output_tile_files": False,
    "z_from_topo": False,
    "receivers_radar_drape": None,
    "receivers_offset_x": 0.0,
    "receivers_offset_y": 0.0,
    "receivers_offset_z": 0.0,
    "gps_receivers_offset": None,
    "ignore_values": None,
    "resolution": None,
    "detrend_order": None,
    "detrend_type": None,
    "max_chunk_size": 128,
    "chunk_by_rows": True,
    "mesh": None,
    "u_cell_size": 25.0,
    "v_cell_size": 25.0,
    "w_cell_size": 25.0,
    "octree_levels_topo": [16, 8, 4, 2],
    "octree_levels_obs": [4, 4, 4, 4],
    "depth_core": 500.0,
    "max_distance": 5000.0,
    "horizontal_padding": 1000.0,
    "vertical_padding": 1000.0,
    "window_center_x": None,
    "window_center_y": None,
    "window_width": None,
    "window_height": None,
    "window_azimuth": None,
    "inversion_style": "voxel",
    "chi_factor": 1.0,
    "sens_wts_threshold": 0.0,
    "every_iteration_bool": False,
    "f_min_change": 1e-4,
    "minGNiter": 1,
    "beta_tol": 0.5,
    "prctile": 95,
    "coolingRate": 1,
    "coolEps_q": True,
    "coolEpsFact": 1.2,
    "beta_search": False,
    "starting_chi_factor": None,
    "max_iterations": 25,
    "max_line_search_iterations": 20,
    "max_cg_iterations": 30,
    "max_global_iterations": 100,
    "initial_beta_ratio": 10.0,
    "initial_beta": None,
    "tol_cg": 1e-4,
    "alpha_s": 1.0,
    "alpha_x": 1.0,
    "alpha_y": 1.0,
    "alpha_z": 1.0,
    "s_norm": 0.0,
    "x_norm": 2.0,
    "y_norm": 2.0,
    "z_norm": 2.0,
    "reference_model_object": None,
    "reference_model": None,
    "gradient_type": "total",
    "lower_bound_object": None,
    "lower_bound": None,
    "upper_bound_object": None,
    "upper_bound": None,
    "parallelized": True,
    "n_cpu": None,
    "max_ram": None,
    "workspace": None,
    "out_group": "GravityInversion",
    "no_data_value": None,
    "monitoring_directory": None,
    "run_command": "geoapps.drivers.grav_inversion",
    "run_command_boolean": False,
    "conda_environment": "geoapps",
}
forward_defaults = {
    "title": "SimPEG Gravity Forward",
    "inversion_type": "gravity",
    "geoh5": None,  # Must remain at top of list for notebook app initialization
    "forward_only": True,
    "topography_object": None,
    "topography": None,
    "data_object": None,
    "gz_channel_bool": False,
    "guv_channel_bool": False,
    "gxy_channel_bool": False,
    "gxx_channel_bool": False,
    "gyy_channel_bool": False,
    "gzz_channel_bool": False,
    "gxz_channel_bool": False,
    "gyz_channel_bool": False,
    "gx_channel_bool": False,
    "gy_channel_bool": False,
    "starting_model_object": None,
    "starting_model": None,
    "tile_spatial": 1,
    "output_tile_files": False,
    "z_from_topo": False,
    "receivers_radar_drape": None,
    "receivers_offset_x": 0.0,
    "receivers_offset_y": 0.0,
    "receivers_offset_z": 0.0,
    "gps_receivers_offset": None,
    "resolution": None,
    "max_chunk_size": 128,
    "chunk_by_rows": True,
    "mesh": None,
    "u_cell_size": 25.0,
    "v_cell_size": 25.0,
    "w_cell_size": 25.0,
    "octree_levels_topo": [16, 8, 4, 2],
    "octree_levels_obs": [4, 4, 4, 4],
    "depth_core": 500.0,
    "max_distance": 5000.0,
    "horizontal_padding": 1000.0,
    "vertical_padding": 1000.0,
    "window_center_x": None,
    "window_center_y": None,
    "window_width": None,
    "window_height": None,
    "window_azimuth": None,
    "parallelized": True,
    "n_cpu": None,
    "workspace": None,
    "out_group": "GravityForward",
    "monitoring_directory": None,
    "run_command": "geoapps.drivers.grav_inversion",
    "run_command_boolean": False,
    "conda_environment": "geoapps",
}

default_ui_json = {
    "title": "SimPEG Gravity Inversion",
    "inversion_type": "gravity",
    "gz_channel_bool": {
        "group": "Data",
        "main": True,
        "label": "Use Gz",
        "value": False,
    },
    "gz_channel": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "label": "Gz channel",
        "parent": "data_object",
        "optional": True,
        "enabled": False,
        "value": None,
    },
    "gz_uncertainty": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "isValue": True,
        "label": "Gz uncertainty (mGal)",
        "parent": "data_object",
        "dependency": "gz_channel",
        "dependencyType": "enabled",
        "property": None,
        "value": 1.0,
    },
    "guv_channel_bool": {
        "group": "Data",
        "main": True,
        "label": "Use Guv",
        "value": False,
    },
    "guv_channel": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "label": "Guv channel",
        "parent": "data_object",
        "optional": True,
        "enabled": False,
        "value": None,
    },
    "guv_uncertainty": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "isValue": True,
        "label": "Guv uncertainty (mGal)",
        "parent": "data_object",
        "dependency": "guv_channel",
        "dependencyType": "enabled",
        "property": None,
        "value": 1.0,
    },
    "gxy_channel_bool": {
        "group": "Data",
        "main": True,
        "label": "Use Gxy (Gne)",
        "value": False,
    },
    "gxy_channel": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "label": "Gxy (Gne) channel",
        "parent": "data_object",
        "optional": True,
        "enabled": False,
        "value": None,
    },
    "gxy_uncertainty": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "isValue": True,
        "label": "Gxy (Gne) uncertainty (mGal)",
        "parent": "data_object",
        "dependency": "gxy_channel",
        "dependencyType": "enabled",
        "property": None,
        "value": 1.0,
    },
    "gxx_channel_bool": {
        "group": "Data",
        "main": True,
        "label": "Use Gxx",
        "value": False,
    },
    "gxx_channel": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "label": "Gxx channel",
        "parent": "data_object",
        "optional": True,
        "enabled": False,
        "value": None,
    },
    "gxx_uncertainty": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "isValue": True,
        "label": "Gxx uncertainty (mGal)",
        "parent": "data_object",
        "dependency": "gxx_channel",
        "dependencyType": "enabled",
        "property": None,
        "value": 1.0,
    },
    "gyy_channel_bool": {
        "group": "Data",
        "main": True,
        "label": "Use Gyy",
        "value": False,
    },
    "gyy_channel": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "label": "Gyy channel",
        "parent": "data_object",
        "optional": True,
        "enabled": False,
        "value": None,
    },
    "gyy_uncertainty": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "isValue": True,
        "label": "Gyy uncertainty (mGal)",
        "parent": "data_object",
        "dependency": "gyy_channel",
        "dependencyType": "enabled",
        "property": None,
        "value": 1.0,
    },
    "gzz_channel_bool": {
        "group": "Data",
        "main": True,
        "label": "Use Gzz",
        "value": False,
    },
    "gzz_channel": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "label": "Gzz channel",
        "parent": "data_object",
        "optional": True,
        "enabled": False,
        "value": None,
    },
    "gzz_uncertainty": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "isValue": True,
        "label": "Gzz uncertainty (mGal)",
        "parent": "data_object",
        "dependency": "gzz_channel",
        "dependencyType": "enabled",
        "property": None,
        "value": 1.0,
    },
    "gxz_channel_bool": {
        "group": "Data",
        "main": True,
        "label": "Use Gxz",
        "value": False,
    },
    "gxz_channel": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "label": "Gxz channel",
        "parent": "data_object",
        "optional": True,
        "enabled": False,
        "value": None,
    },
    "gxz_uncertainty": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "isValue": True,
        "label": "Gxz uncertainty (mGal)",
        "parent": "data_object",
        "dependency": "gxz_channel",
        "dependencyType": "enabled",
        "property": None,
        "value": 1.0,
    },
    "gyz_channel_bool": {
        "group": "Data",
        "main": True,
        "label": "Use Gyz",
        "value": False,
    },
    "gyz_channel": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "label": "Gyz channel",
        "parent": "data_object",
        "optional": True,
        "enabled": False,
        "value": None,
    },
    "gyz_uncertainty": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "isValue": True,
        "label": "Gyz uncertainty (mGal)",
        "parent": "data_object",
        "dependency": "gyz_channel",
        "dependencyType": "enabled",
        "property": None,
        "value": 1.0,
    },
    "gx_channel_bool": {
        "group": "Data",
        "main": True,
        "label": "Use Gx",
        "value": False,
    },
    "gx_channel": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "label": "Gx channel",
        "parent": "data_object",
        "optional": True,
        "enabled": False,
        "value": None,
    },
    "gx_uncertainty": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "isValue": True,
        "label": "Gx uncertainty (mGal)",
        "parent": "data_object",
        "dependency": "gx_channel",
        "dependencyType": "enabled",
        "property": None,
        "value": 1.0,
    },
    "gy_channel_bool": {
        "group": "Data",
        "main": True,
        "label": "Use Gy",
        "value": False,
    },
    "gy_channel": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "label": "Gy channel",
        "parent": "data_object",
        "optional": True,
        "enabled": False,
        "value": None,
    },
    "gy_uncertainty": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "isValue": True,
        "label": "Gy uncertainty (mGal)",
        "parent": "data_object",
        "dependency": "gy_channel",
        "dependencyType": "enabled",
        "property": None,
        "value": 1.0,
    },
    "starting_model": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Starting Model",
        "main": True,
        "isValue": False,
        "parent": "starting_model_object",
        "label": "Density (g/cc)",
        "property": None,
        "value": 0.0,
    },
    "out_group": {"label": "Results group name", "value": "Gravity"},
}

base_default_ui_json.update(default_ui_json)
default_ui_json = base_default_ui_json.copy()
for k, v in inversion_defaults.items():
    if isinstance(default_ui_json[k], dict):
        key = "value"
        if "isValue" in default_ui_json[k].keys():
            if default_ui_json[k]["isValue"] == False:
                key = "property"
        if "enabled" in default_ui_json[k].keys() and v is not None:
            default_ui_json[k]["enabled"] = True
        default_ui_json[k][key] = v
    else:
        default_ui_json[k] = v

default_ui_json = {k: default_ui_json[k] for k in inversion_defaults}


################ Validations #################

required_parameters = ["inversion_type"]
required_parameters += base_required_parameters

validations = {
    "inversion_type": {
        "types": [str],
        "values": ["gravity"],
    },
    "gz_channel_bool": {"types": [bool]},
    "gz_channel": {
        "types": [str, UUID],
    },
    "gz_uncertainty": {
        "types": [str, int, float, UUID],
    },
    "guv_channel_bool": {"types": [bool]},
    "guv_channel": {
        "types": [str, UUID],
    },
    "guv_uncertainty": {
        "types": [str, int, float, UUID],
    },
    "gxy_channel_bool": {"types": [bool]},
    "gxy_channel": {
        "types": [str, UUID],
    },
    "gxy_uncertainty": {
        "types": [str, int, float, UUID],
    },
    "gxx_channel_bool": {"types": [bool]},
    "gxx_channel": {
        "types": [str, UUID],
    },
    "gxx_uncertainty": {
        "types": [str, int, float, UUID],
    },
    "gyy_channel_bool": {"types": [bool]},
    "gyy_channel": {
        "types": [str, UUID],
    },
    "gyy_uncertainty": {
        "types": [str, int, float, UUID],
    },
    "gzz_channel_bool": {"types": [bool]},
    "gzz_channel": {
        "types": [str, UUID],
    },
    "gzz_uncertainty": {
        "types": [str, int, float, UUID],
    },
    "gxz_channel_bool": {"types": [bool]},
    "gxz_channel": {
        "types": [str, UUID],
    },
    "gxz_uncertainty": {
        "types": [str, int, float, UUID],
    },
    "gyz_channel_bool": {"types": [bool]},
    "gyz_channel": {
        "types": [str, UUID],
    },
    "gyz_uncertainty": {
        "types": [str, int, float, UUID],
    },
    "gx_channel_bool": {"types": [bool]},
    "gx_channel": {
        "types": [str, UUID],
    },
    "gx_uncertainty": {
        "types": [str, int, float, UUID],
    },
    "gy_channel_bool": {"types": [bool]},
    "gy_channel": {
        "types": [str, UUID],
    },
    "gy_uncertainty": {
        "types": [str, int, float, UUID],
    },
    "out_group": {"types": [str, ContainerGroup]},
}
validations.update(base_validations)
