#  Copyright (c) 2023 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

from __future__ import annotations

from uuid import UUID

from geoh5py.objects.surveys.direct_current import PotentialElectrode

import geoapps
from geoapps import assets_path
from geoapps.inversion import default_ui_json as base_default_ui_json
from geoapps.inversion.constants import validations as base_validations

inversion_defaults = {
    "version": geoapps.__version__,
    "title": "Induced Polarization (IP) 2D Inversion",
    "icon": "PotentialElectrode",
    "inversion_type": "induced polarization 2d",
    "geoh5": None,  # Must remain at top of list for notebook app initialization
    "forward_only": False,
    "topography_object": None,
    "topography": None,
    "data_object": None,
    "z_from_topo": True,
    "line_object": None,
    "line_id": 1,
    "resolution": None,
    "receivers_radar_drape": None,
    "receivers_offset_z": None,
    "gps_receivers_offset": None,
    "chargeability_channel": None,
    "chargeability_uncertainty": 1.0,
    "mesh": None,
    "conductivity_model": 1e-3,
    "starting_model": None,
    "reference_model": None,
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
    "initial_beta_ratio": 10.0,
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
    "prctile": 95,
    "coolEps_q": True,
    "coolEpsFact": 1.2,
    "beta_search": False,
    "sens_wts_threshold": 30.0,
    "every_iteration_bool": True,
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
    "version": geoapps.__version__,
    "title": "Induced Polarization (IP) 2D Forward",
    "icon": "PotentialElectrode",
    "inversion_type": "induced polarization 2d",
    "geoh5": None,  # Must remain at top of list for notebook app initialization
    "forward_only": True,
    "topography_object": None,
    "topography": None,
    "data_object": None,
    "resolution": None,
    "z_from_topo": True,
    "line_object": None,
    "line_id": 1,
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
    "line_object": {
        "association": ["Cell", "Vertex"],
        "dataType": "Referenced",
        "group": "Survey",
        "main": True,
        "label": "Line ID",
        "parent": "data_object",
        "value": None,
    },
    "line_id": {
        "group": "Survey",
        "main": True,
        "min": 1,
        "label": "Line number",
        "value": 1,
    },
    "data_object": {
        "main": True,
        "group": "Survey",
        "label": "Object",
        "meshType": "{275ecee9-9c24-4378-bf94-65f3c5fbe163}",
        "value": None,
    },
    "z_from_topo": {
        "group": "Survey",
        "main": True,
        "label": "Surface survey",
        "tooltip": "Uncheck if borehole data is present",
        "value": True,
    },
    "chargeability_channel": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Survey",
        "main": True,
        "label": "Chargeability (V/V)",
        "parent": "data_object",
        "value": None,
    },
    "chargeability_uncertainty": {
        "association": ["Cell", "Vertex"],
        "dataType": "Float",
        "group": "Survey",
        "main": True,
        "isValue": True,
        "label": "Uncertainty",
        "parent": "data_object",
        "property": None,
        "value": 1.0,
    },
    "starting_model": {
        "association": "Cell",
        "dataType": "Float",
        "group": "Mesh and models",
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
    "title": "Induced Polarization (IP) 2D Inversion",
    "icon": "PotentialElectrode",
    "inversion_type": "induced polarization 2d",
    "line_object": {
        "association": ["Cell", "Vertex"],
        "dataType": "Referenced",
        "group": "Data",
        "main": True,
        "label": "Line ID",
        "parent": "data_object",
        "value": None,
    },
    "line_id": {
        "group": "Data",
        "main": True,
        "min": 1,
        "label": "Line number",
        "value": 1,
    },
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
    "mesh": {
        "group": "Mesh and models",
        "main": True,
        "optional": True,
        "enabled": False,
        "label": "Mesh",
        "meshType": "{C94968EA-CF7D-11EB-B8BC-0242AC130003}",
        "value": None,
    },
    "conductivity_model": {
        "association": "Cell",
        "dataType": "Float",
        "group": "Mesh and models",
        "main": True,
        "isValue": True,
        "parent": "mesh",
        "label": "Conductivity (S/m)",
        "property": None,
        "value": 1e-3,
    },
    "starting_model": {
        "association": "Cell",
        "dataType": "Float",
        "group": "Mesh and models",
        "main": True,
        "isValue": False,
        "parent": "mesh",
        "label": "Initial chargeability (V/V)",
        "property": None,
        "value": 0.0,
    },
    "reference_model": {
        "association": "Cell",
        "dataType": "Float",
        "main": True,
        "group": "Mesh and models",
        "isValue": True,
        "parent": "mesh",
        "label": "Reference chargeability (V/V)",
        "property": None,
        "value": 0.0,
    },
    "lower_bound": {
        "association": "Cell",
        "main": True,
        "dataType": "Float",
        "group": "Mesh and models",
        "isValue": True,
        "parent": "mesh",
        "label": "Lower bound (V/V)",
        "property": None,
        "optional": True,
        "value": 0,
        "enabled": False,
    },
    "upper_bound": {
        "association": "Cell",
        "main": True,
        "dataType": "Float",
        "group": "Mesh and models",
        "isValue": True,
        "parent": "mesh",
        "label": "Upper bound (V/V)",
        "property": None,
        "optional": True,
        "value": 100.0,
        "enabled": False,
    },
    "window_center_x": {
        "group": "Data window",
        "enabled": False,
        "groupOptional": True,
        "label": "Window center easting",
        "value": 0.0,
        "visible": False,
    },
    "window_center_y": {
        "group": "Data window",
        "enabled": False,
        "label": "Window center northing",
        "value": 0.0,
        "visible": False,
    },
    "window_width": {
        "min": 0.0,
        "group": "Data window",
        "enabled": False,
        "label": "Window width",
        "value": 0.0,
        "visible": False,
    },
    "window_height": {
        "min": 0.0,
        "group": "Data window",
        "enabled": False,
        "label": "Window height",
        "value": 0.0,
        "visible": False,
    },
    "window_azimuth": {
        "min": -180,
        "max": 180,
        "group": "Data window",
        "enabled": False,
        "label": "Window azimuth",
        "value": 0.0,
        "visible": False,
    },
    "resolution": None,
    "detrend_order": None,
    "detrend_type": None,
    "tile_spatial": 1,
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


################ Validations #################

validations = {
    "inversion_type": {
        "required": True,
        "values": ["induced polarization 2d"],
    },
    "data_object": {"required": True, "types": [UUID, PotentialElectrode]},
}

validations = dict(base_validations, **validations)

app_initializer = {
    "geoh5": str(assets_path() / "FlinFlon_dcip.geoh5"),
    "data_object": UUID("{6e14de2c-9c2f-4976-84c2-b330d869cb82}"),
    "chargeability_channel": UUID("{162320e6-2b80-4877-9ec1-a8f5b6a13673}"),
    "chargeability_uncertainty": 0.001,
    "line_object": UUID("{d400e8f1-8460-4609-b852-b3b93f945770}"),
    "line_id": 5,
    "mesh": UUID("{537cdf17-28c9-4baa-a1ac-07c37662583d}"),
    "starting_model": 1e-4,
    "conductivity_model": 0.1,
    "resolution": None,
    "window_center_x": None,
    "window_center_y": None,
    "window_width": None,
    "window_height": None,
    "window_azimuth": None,
    "s_norm": 0.0,
    "x_norm": 2.0,
    "y_norm": 2.0,
    "z_norm": 2.0,
    "upper_bound": 100.0,
    "lower_bound": 1e-5,
    "max_global_iterations": 25,
    "topography_object": UUID("{ab3c2083-6ea8-4d31-9230-7aad3ec09525}"),
    "topography": UUID("{a603a762-f6cb-4b21-afda-3160e725bf7d}"),
    "z_from_topo": True,
    "receivers_offset_z": 0.0,
}
