#  Copyright (c) 2022 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

from __future__ import annotations

import base64
import io
import os
from time import time

import numpy as np
from dash import callback_context, dcc, html
from dash.dependencies import Input, Output
from discretize.utils import mesh_utils
from geoh5py.objects import BlockModel
from geoh5py.objects.object_base import ObjectBase
from geoh5py.ui_json import InputFile
from geoh5py.workspace import Workspace

from geoapps.base.dash_application import BaseDashApplication
from geoapps.grid_creation.constants import app_initializer
from geoapps.grid_creation.driver import GridCreationDriver
from geoapps.grid_creation.params import GridCreationParams


class GridCreation(BaseDashApplication):
    _param_class = GridCreationParams

    def __init__(self, ui_json=None, **kwargs):
        app_initializer.update(kwargs)
        if ui_json is not None and os.path.exists(ui_json.path):
            self.params = self._param_class(ui_json)
        else:
            self.params = self._param_class(**app_initializer)

        super().__init__(**kwargs)

        # Initial values for the dash components
        defaults = self.get_defaults()

        # Set up the layout with the dash components
        self.app.layout = html.Div(
            [
                dcc.Upload(
                    id="upload",
                    children=html.Button("Upload Workspace/ui.json"),
                    style={"margin_bottom": "20px"},
                ),
                dcc.Markdown(
                    children="Input object",
                    style={"width": "25%", "display": "inline-block"},
                ),
                dcc.Dropdown(
                    id="objects",
                    value=defaults["objects_name"],
                    options=defaults["objects_options"],
                    style={
                        "width": "75%",
                        "display": "inline-block",
                        "margin_bottom": "20px",
                    },
                ),
                dcc.Markdown(
                    children="Lateral extent",
                    style={"width": "25%", "display": "inline-block"},
                ),
                dcc.Dropdown(
                    id="xy_reference",
                    value=defaults["xy_reference_name"],
                    options=defaults["xy_reference_options"],
                    style={
                        "width": "75%",
                        "display": "inline-block",
                        "margin_bottom": "20px",
                    },
                ),
                dcc.Markdown(
                    children="Name",
                    style={"width": "25%", "display": "inline-block"},
                ),
                dcc.Input(
                    id="new_grid",
                    value=defaults["new_grid"],
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "margin_bottom": "20px",
                    },
                ),
                dcc.Markdown(
                    children="Minimum x cell size",
                    style={"width": "25%", "display": "inline-block"},
                ),
                dcc.Input(
                    id="cell_size_x",
                    value=defaults["cell_size_x"],
                    type="number",
                    min=0.0,
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "margin_bottom": "20px",
                    },
                ),
                dcc.Markdown(
                    children="Minimum y cell size",
                    style={"width": "25%", "display": "inline-block"},
                ),
                dcc.Input(
                    id="cell_size_y",
                    value=defaults["cell_size_y"],
                    type="number",
                    min=0.0,
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "margin_bottom": "20px",
                    },
                ),
                dcc.Markdown(
                    children="Minimum z cell size",
                    style={"width": "25%", "display": "inline-block"},
                ),
                dcc.Input(
                    id="cell_size_z",
                    value=defaults["cell_size_z"],
                    type="number",
                    min=0.0,
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "margin_bottom": "20px",
                    },
                ),
                dcc.Markdown(
                    children="Core depth (m)",
                    style={"width": "25%", "display": "inline-block"},
                ),
                dcc.Input(
                    id="depth_core",
                    type="number",
                    value=defaults["depth_core"],
                    min=0.0,
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "margin_bottom": "20px",
                    },
                ),
                dcc.Markdown(
                    children="Horizontal padding",
                    style={"width": "25%", "display": "inline-block"},
                ),
                dcc.Input(
                    id="horizontal_padding",
                    value=defaults["horizontal_padding"],
                    type="number",
                    min=0.0,
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "margin_bottom": "20px",
                    },
                ),
                dcc.Markdown(
                    children="Bottom padding",
                    style={"width": "25%", "display": "inline-block"},
                ),
                dcc.Input(
                    id="bottom_padding",
                    value=defaults["bottom_padding"],
                    type="number",
                    min=0.0,
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "margin_bottom": "20px",
                    },
                ),
                dcc.Markdown(
                    children="Expansion factor",
                    style={"width": "25%", "display": "inline-block"},
                ),
                dcc.Input(
                    id="expansion_fact",
                    type="number",
                    value=defaults["expansion_fact"],
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "margin_bottom": "20px",
                    },
                ),
                dcc.Markdown(
                    children="Monitoring directory",
                    style={"width": "25%", "display": "inline-block"},
                ),
                dcc.Input(
                    id="monitoring_directory",
                    value=os.path.abspath(defaults["monitoring_directory"]),
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "margin_bottom": "20px",
                    },
                ),
                dcc.Checklist(
                    id="live_link",
                    options=["Geoscience ANALYST Pro - Live link"],
                    value=[],
                    style={"margin_bottom": "20px"},
                ),
                html.Button("Export", id="export"),
                dcc.Markdown(id="output_message"),
            ],
            style={
                "margin_left": "20px",
                "margin_top": "20px",
                "width": "75%",
            },
        )

        # Set up callbacks
        self.app.callback(
            Output(component_id="new_grid", component_property="value"),
            Output(component_id="objects", component_property="value"),
            Output(component_id="objects", component_property="options"),
            Output(component_id="xy_reference", component_property="value"),
            Output(component_id="xy_reference", component_property="options"),
            Output(component_id="cell_size_x", component_property="value"),
            Output(component_id="cell_size_y", component_property="value"),
            Output(component_id="cell_size_z", component_property="value"),
            Output(component_id="depth_core", component_property="value"),
            Output(component_id="horizontal_padding", component_property="value"),
            Output(component_id="bottom_padding", component_property="value"),
            Output(component_id="expansion_fact", component_property="value"),
            Output(component_id="monitoring_directory", component_property="value"),
            Output(component_id="upload", component_property="filename"),
            Output(component_id="upload", component_property="contents"),
            Input(component_id="upload", component_property="filename"),
            Input(component_id="upload", component_property="contents"),
            Input(component_id="new_grid", component_property="value"),
            Input(component_id="objects", component_property="value"),
            Input(component_id="xy_reference", component_property="value"),
            Input(component_id="cell_size_x", component_property="value"),
            Input(component_id="cell_size_y", component_property="value"),
            Input(component_id="cell_size_z", component_property="value"),
            Input(component_id="depth_core", component_property="value"),
            Input(component_id="horizontal_padding", component_property="value"),
            Input(component_id="bottom_padding", component_property="value"),
            Input(component_id="expansion_fact", component_property="value"),
            Input(component_id="live_link", component_property="value"),
            Input(component_id="monitoring_directory", component_property="value"),
        )(self.update_params)
        self.app.callback(
            Output(component_id="live_link", component_property="value"),
            Input(component_id="export", component_property="n_clicks"),
            prevent_initial_call=True,
        )(self.create_block_model)

    @staticmethod
    def truncate_locs_depths(locs: np.ndarray, depth_core: int):
        """
        Sets locations below core to core bottom.
        :param locs: Location points.
        :param depth_core: Depth of core mesh below locs.
        :return locs: locs with depths truncated.
        """
        zmax = locs[:, 2].max()  # top of locs
        below_core_ind = (zmax - locs[:, 2]) > depth_core
        core_bottom_elev = zmax - depth_core
        locs[
            below_core_ind, 2
        ] = core_bottom_elev  # sets locations below core to core bottom
        return locs

    @staticmethod
    def minimum_depth_core(locs: np.ndarray, depth_core: int, core_z_cell_size: int):
        """
        Get minimum depth core.
        :param locs: Location points.
        :param depth_core: Depth of core mesh below locs.
        :param core_z_cell_size: Cell size in z direction.
        :return depth_core: Minimum depth core.
        """
        zrange = locs[:, 2].max() - locs[:, 2].min()  # locs z range
        if depth_core >= zrange:
            return depth_core - zrange + core_z_cell_size
        else:
            return depth_core

    @staticmethod
    def find_top_padding(obj: BlockModel, core_z_cell_size: int):
        """
        Loop through cell spacing and sum until core_z_cell_size is reached.
        :param obj: Block model.
        :param core_z_cell_size: Cell size in z direction.
        :return pad_sum: Top padding.
        """
        f = np.abs(np.diff(obj.z_cell_delimiters))
        pad_sum = 0
        for h in np.abs(np.diff(obj.z_cell_delimiters)):
            if h != core_z_cell_size:
                pad_sum += h
            else:
                return pad_sum

    @staticmethod
    def get_block_model(
        workspace: Workspace,
        name: str,
        locs: np.ndarray,
        h: list,
        depth_core: int,
        pads: list,
        expansion_factor: float,
    ):
        """
        Get block model.
        :param workspace: Workspace.
        :param name: Block model name.
        :param locs: Location points.
        :param h: Cell size(s) for the core mesh.
        :param depth_core: Depth of core mesh below locs.
        :param pads: len(6) Padding distances [W, E, N, S, Down, Up]
        :param expansion_factor: Expansion factor for padding cells.
        :return object_out: Output block model.
        """

        locs = GridCreation.truncate_locs_depths(locs, depth_core)
        depth_core = GridCreation.minimum_depth_core(locs, depth_core, h[2])
        mesh = mesh_utils.mesh_builder_xyz(
            locs,
            h,
            padding_distance=[
                [pads[0], pads[1]],
                [pads[2], pads[3]],
                [pads[4], pads[5]],
            ],
            depth_core=depth_core,
            expansion_factor=expansion_factor,
        )

        object_out = BlockModel.create(
            workspace,
            origin=[mesh.x0[0], mesh.x0[1], locs[:, 2].max()],
            u_cell_delimiters=mesh.vectorNx - mesh.x0[0],
            v_cell_delimiters=mesh.vectorNy - mesh.x0[1],
            z_cell_delimiters=-(mesh.x0[2] + mesh.hz.sum() - mesh.vectorNz[::-1]),
            name=name,
        )

        top_padding = GridCreation.find_top_padding(object_out, h[2])
        object_out.origin["z"] += top_padding

        return object_out

    def update_params(
        self,
        filename,
        contents,
        new_grid,
        objects,
        xy_reference,
        cell_size_x,
        cell_size_y,
        cell_size_z,
        depth_core,
        horizontal_padding,
        bottom_padding,
        expansion_fact,
        live_link,
        monitoring_directory,
    ):
        param_list = [
            "new_grid",
            "objects_name",
            "objects_options",
            "xy_reference_name",
            "xy_reference_options",
            "call_size_x",
            "call_size_y",
            "call_size_z",
            "depth_core",
            "horizontal_padding",
            "bottom_padding",
            "expansion_fact",
            "monitoring_directory",
            "filename",
            "contents",
        ]
        cell_size_x, cell_size_y, cell_size_z = (
            float(cell_size_x),
            float(cell_size_y),
            float(cell_size_z),
        )
        horizontal_padding, bottom_padding = float(horizontal_padding), float(
            bottom_padding
        )
        depth_core, expansion_fact = float(depth_core), float(expansion_fact)

        trigger = callback_context.triggered[0]["prop_id"].split(".")[0]
        update_dict = {}
        if trigger == "upload":
            if (filename.endswith("ui.json") or filename.endswith(".geoh5")) and (
                contents is not None
            ):
                if filename.endswith(".ui.json"):
                    update_dict.update(self.update_from_ui_json(contents, param_list))
                    ws = update_dict["geoh5"]
                elif filename.endswith(".geoh5"):
                    content_type, content_string = contents.split(",")
                    decoded = io.BytesIO(base64.b64decode(content_string))
                    ws = Workspace(decoded)
                update_dict.update(self.update_object_options(ws, "objects"))
                update_dict.update(self.update_object_options(ws, "xy_reference"))
                update_dict["filename"] = None
                update_dict["contents"] = None
            else:
                print("Uploaded file must be a workspace or ui.json.")
        elif trigger + "_name" in param_list:
            update_dict[trigger + "_name"] = locals()[trigger]
        elif trigger != "":
            update_dict[trigger] = locals()[trigger]

        self.update_param_dict(update_dict)
        outputs = self.get_outputs(param_list, update_dict)

        return outputs

    def create_block_model(self, n_clicks):
        # self.params should be up to date whenever create_block_model is called.
        param_dict = self.params.to_dict()
        temp_geoh5 = f"BlockModel_{time():.0f}.geoh5"

        # Get output path.
        if self.params.live_link:
            if self.params.monitoring_directory is not None and os.path.exists(
                os.path.abspath(self.params.monitoring_directory)
            ):
                output_path = self.params.monitoring_directory
            else:
                print("Invalid monitoring directory path")
                return []
        else:
            output_path = os.path.dirname(self.params.geoh5.h5file)

        # Get output workspace.
        ws, self.params.live_link = self.get_output_workspace(
            self.params.live_link, output_path, temp_geoh5
        )
        with ws as workspace:
            # Put entities in output workspace.
            param_dict["geoh5"] = workspace
            for key, value in param_dict.items():
                if isinstance(value, ObjectBase):
                    param_dict[key] = value.copy(parent=workspace, copy_children=True)

            # Write output uijson.
            ifile = InputFile(
                ui_json=self.params.input_file.ui_json,
                validation_options={"disabled": True},
            )
            new_params = GridCreationParams(input_file=ifile, **param_dict)
            new_params.write_input_file(
                name=temp_geoh5.replace(".geoh5", ".ui.json"),
                path=output_path,
                validate=False,
            )
            # Run driver.
            driver = GridCreationDriver(new_params)
            driver.run()

        if self.params.live_link:
            print("Live link active. Check your ANALYST session for new mesh.")
            return ["Geoscience ANALYST Pro - Live link"]
        else:
            print("Saved to " + os.path.abspath(output_path))
            return []