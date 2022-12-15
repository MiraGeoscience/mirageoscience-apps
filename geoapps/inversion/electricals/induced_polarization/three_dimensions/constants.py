#  Copyright (c) 2022 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

from __future__ import annotations

from uuid import UUID

from geoh5py.objects.surveys.direct_current import PotentialElectrode

from geoapps.inversion import default_ui_json as base_default_ui_json

inversion_defaults = {
    "title": "Induced Polarization 3D inversion",
    "documentation": "https://geoapps.readthedocs.io/en/stable/content/applications/dcip_inversion.html",
    "icon": "PotentialElectrode",
    "inversion_type": "induced polarization 3d",
    "geoh5": None,  # Must remain at top of list for notebook app initialization
    "forward_only": False,
    "topography_object": None,
    "topography": None,
    "data_object": None,
    "resolution": None,
    "z_from_topo": True,
    "receivers_radar_drape": None,
    "receivers_offset_z": None,
    "gps_receivers_offset": None,
    "chargeability_channel": None,
    "chargeability_uncertainty": 1.0,
    "mesh": None,
    "conductivity_model": 1e-3,
    "starting_model": 0.0,
    "reference_model": 0.0,
    "lower_bound": None,
    "upper_bound": None,
    "output_tile_files": False,
    "ignore_values": None,
    "detrend_order": None,
    "detrend_type": None,
    "window_center_x": None,
    "window_center_y": None,
    "window_width": None,
    "window_height": None,
    "window_azimuth": None,
    "inversion_style": "voxel",
    "chi_factor": 1.0,
    "initial_beta_ratio": 1e1,
    "initial_beta": None,
    "coolingRate": 2,
    "coolingFactor": 2.0,
    "max_global_iterations": 50,
    "max_line_search_iterations": 20,
    "max_cg_iterations": 30,
    "tol_cg": 1e-4,
    "alpha_s": 1.0,
    "alpha_x": 1.0,
    "alpha_y": 1.0,
    "alpha_z": 1.0,
    "s_norm": 0.0,
    "x_norm": 2.0,
    "y_norm": 2.0,
    "z_norm": 2.0,
    "gradient_type": "total",
    "max_irls_iterations": 25,
    "starting_chi_factor": None,
    "f_min_change": 1e-4,
    "beta_tol": 0.5,
    "prctile": 50,
    "coolEps_q": True,
    "coolEpsFact": 1.2,
    "beta_search": False,
    "sens_wts_threshold": 1e-3,
    "every_iteration_bool": False,
    "parallelized": True,
    "n_cpu": None,
    "tile_spatial": 1,
    "max_ram": None,
    "store_sensitivities": "ram",
    "max_chunk_size": 128,
    "chunk_by_rows": True,
    "out_group": "InducedPolarizationInversion",
    "generate_sweep": False,
    "monitoring_directory": None,
    "workspace_geoh5": None,
    "run_command": "geoapps.inversion.driver",
    "conda_environment": "geoapps",
    "distributed_workers": None,
    "chargeability_channel_bool": True,
}

forward_defaults = {
    "title": "Induced Polarization 3D forward",
    "documentation": "https://geoapps.readthedocs.io/en/stable/content/applications/dcip_inversion.html",
    "icon": "PotentialElectrode",
    "inversion_type": "induced polarization 3d",
    "geoh5": None,  # Must remain at top of list for notebook app initialization
    "forward_only": True,
    "topography_object": None,
    "topography": None,
    "data_object": None,
    "resolution": None,
    "z_from_topo": True,
    "receivers_radar_drape": None,
    "receivers_offset_z": None,
    "gps_receivers_offset": None,
    "chargeability_channel_bool": True,
    "mesh": None,
    "conductivity_model": 1e-3,
    "starting_model": None,
    "output_tile_files": False,
    "window_center_x": None,
    "window_center_y": None,
    "window_width": None,
    "window_height": None,
    "window_azimuth": None,
    "parallelized": True,
    "n_cpu": None,
    "tile_spatial": 1,
    "max_chunk_size": 128,
    "chunk_by_rows": True,
    "out_group": "InducedPolarizationForward",
    "generate_sweep": False,
    "monitoring_directory": None,
    "workspace_geoh5": None,
    "run_command": "geoapps.inversion.driver",
    "conda_environment": "geoapps",
    "distributed_workers": None,
    "gradient_type": "total",
    "alpha_s": 1.0,
    "alpha_x": 1.0,
    "alpha_y": 1.0,
    "alpha_z": 1.0,
    "s_norm": 0.0,
    "x_norm": 2.0,
    "y_norm": 2.0,
    "z_norm": 2.0,
}
inversion_ui_json = {
    "chargeability_channel_bool": True,
}

forward_ui_json = {
    "starting_model": {
        "association": "Cell",
        "dataType": "Float",
        "group": "Mesh and Models",
        "main": True,
        "isValue": False,
        "parent": "mesh",
        "label": "Chargeability (V/V)",
        "property": None,
        "value": 0.0,
    },
    "gradient_type": "total",
    "alpha_s": 1.0,
    "alpha_x": 1.0,
    "alpha_y": 1.0,
    "alpha_z": 1.0,
    "s_norm": 0.0,
    "x_norm": 2.0,
    "y_norm": 2.0,
    "z_norm": 2.0,
}
default_ui_json = {
    "title": "Induced Polarization 3D inversion",
    "documentation": "https://geoapps.readthedocs.io/en/stable/content/applications/dcip_inversion.html",
    "icon": "PotentialElectrode",
    "inversion_type": "induced polarization 3d",
    "data_object": {
        "main": True,
        "group": "Data",
        "label": "Object",
        "meshType": "{275ecee9-9c24-4378-bf94-65f3c5fbe163}",
        "value": None,
    },
    "z_from_topo": {
        "group": "Data",
        "main": True,
        "label": "Surface survey",
        "tooltip": "Uncheck if borehole data is present",
        "value": True,
    },
    "chargeability_channel_bool": True,
    "chargeability_channel": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "label": "Chargeability (V/V)",
        "parent": "data_object",
        "value": None,
    },
    "chargeability_uncertainty": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data",
        "main": True,
        "isValue": True,
        "label": "Uncertainty",
        "parent": "data_object",
        "property": None,
        "value": 1.0,
    },
    "starting_model": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Mesh and Models",
        "main": True,
        "isValue": False,
        "parent": "mesh",
        "label": "Initial Chargeability (V/V)",
        "property": None,
        "value": 0.0,
    },
    "reference_model": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "main": True,
        "group": "Mesh and Models",
        "isValue": True,
        "parent": "mesh",
        "label": "Reference Chargeability (V/V)",
        "property": None,
        "value": 0.0,
    },
    "conductivity_model": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Mesh and Models",
        "main": True,
        "isValue": True,
        "parent": "mesh",
        "label": "Conductivity (S/m)",
        "property": None,
        "value": 1e-3,
    },
    "lower_bound": {
        "association": ["Cell", "Vertex"],
        "main": True,
        "dataType": "Float",
        "group": "Mesh and Models",
        "isValue": True,
        "parent": "mesh",
        "label": "Lower bound (V/V)",
        "property": None,
        "optional": True,
        "value": 0,
        "enabled": False,
    },
    "upper_bound": {
        "association": ["Cell", "Vertex"],
        "main": True,
        "dataType": "Float",
        "group": "Mesh and Models",
        "isValue": True,
        "parent": "mesh",
        "label": "Upper bound (V/V",
        "property": None,
        "optional": True,
        "value": 100.0,
        "enabled": False,
    },
    "resolution": None,
    "detrend_order": None,
    "detrend_type": None,
    "out_group": {
        "label": "Results group name",
        "value": "InducedPolarizationInversion",
    },
    "receivers_offset_z": {
        "group": "Data pre-processing",
        "label": "Z static offset",
        "optional": True,
        "enabled": False,
        "value": 0.0,
        "visible": False,
    },
    "receivers_radar_drape": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Data pre-processing",
        "label": "Z radar offset",
        "tooltip": "Apply a non-homogeneous offset to survey object from radar channel.",
        "optional": True,
        "parent": "data_object",
        "value": None,
        "enabled": False,
        "visible": False,
    },
}

default_ui_json = dict(base_default_ui_json, **default_ui_json)


################ Validations ##################

validations = {
    "inversion_type": {
        "required": True,
        "values": ["induced polarization 3d"],
    },
    "conductivity_model": {"required": True},
    "data_object": {"required": True, "types": [UUID, PotentialElectrode]},
}

app_initializer = {
    "geoh5": "../../../assets/FlinFlon_dcip.geoh5",
    "data_object": UUID("{6e14de2c-9c2f-4976-84c2-b330d869cb82}"),
    "chargeability_channel": UUID("{162320e6-2b80-4877-9ec1-a8f5b6a13673}"),
    "chargeability_uncertainty": 0.001,
    "mesh": UUID("{da109284-aa8c-4824-a647-29951109b058}"),
    "starting_model": 1e-4,
    "conductivity_model": 0.1,
    "resolution": None,
    "window_center_x": None,
    "window_center_y": None,
    "window_width": None,
    "window_height": None,
    "window_azimuth": None,
    "octree_levels_topo": [0, 0, 4, 4],
    "octree_levels_obs": [4, 4, 4, 4],
    "depth_core": 1200.0,
    "horizontal_padding": 1000.0,
    "vertical_padding": 1000.0,
    "s_norm": 0.0,
    "x_norm": 2.0,
    "y_norm": 2.0,
    "z_norm": 2.0,
    "max_global_iterations": 25,
    "topography_object": UUID("{ab3c2083-6ea8-4d31-9230-7aad3ec09525}"),
    "topography": UUID("{a603a762-f6cb-4b21-afda-3160e725bf7d}"),
    "z_from_topo": True,
    "receivers_offset_z": 0.0,
}
