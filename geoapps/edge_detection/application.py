# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of geoapps.                                               '
#                                                                              '
#  geoapps is distributed under the terms and conditions of the MIT License    '
#  (see LICENSE file at the root of this source code package).                 '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from __future__ import annotations

import warnings
from pathlib import Path
from time import time
from uuid import UUID

from curve_apps.edges.driver import EdgesDriver
from curve_apps.edges.params import EdgeParameters
from geoh5py import Workspace
from geoh5py.data import FloatData
from geoh5py.objects import Grid2D, ObjectBase
from geoh5py.shared.utils import fetch_active_workspace
from geoh5py.ui_json import InputFile

from geoapps import assets_path
from geoapps.base.application import BaseApplication
from geoapps.base.plot import PlotSelection2D
from geoapps.shared_utils.utils import filter_xy
from geoapps.utils import warn_module_not_found
from geoapps.utils.formatters import string_name


with warn_module_not_found():
    from ipywidgets import (
        Button,
        FloatSlider,
        HBox,
        IntSlider,
        Layout,
        Text,
        VBox,
        Widget,
    )

with warn_module_not_found():
    from matplotlib import collections


class EdgeDetectionApp(PlotSelection2D):
    """
    Widget for Grid2D objects for the automated detection of line features.
    The application relies on the Canny and Hough transforms from the
    Scikit-Image library.

    :param grid: Grid2D object
    :param data: Children data object for the provided grid

    Optional
    --------

    :param sigma [Canny]: standard deviation of the Gaussian filter
    :param threshold [Hough]: Value threshold
    :param line_length [Hough]: Minimum accepted pixel length of detected lines
    :param line_gap [Hough]: Maximum gap between pixels to still form a line.
    """

    _object_types = (Grid2D,)
    _param_class = EdgeParameters
    _initializer = {
        "geoh5": str(assets_path() / "FlinFlon.geoh5"),
        "objects": UUID("{538a7eb1-2218-4bec-98cc-0a759aa0ef4f}"),
        "data": UUID("{44822654-b6ae-45b0-8886-2d845f80f422}"),
        "line_length": 1,
        "line_gap": 1,
        "sigma": 0.5,
        "threshold": 1,
        "window_size": None,
        "merge_length": None,
        "export_as": "Edges",
        "out_group": None,
    }

    def __init__(self, ui_json=None, plot_result=True, geoh5: str | None = None):
        defaults = {}

        if isinstance(geoh5, str):
            if Path(geoh5).exists():
                defaults["geoh5"] = geoh5
            else:
                warnings.warn("Path provided in 'geoh5' argument does not exist.")

        if ui_json is not None:
            if isinstance(ui_json, str):
                if not Path(ui_json).exists():
                    raise FileNotFoundError(
                        f"Provided uijson path {ui_json} not does not exist."
                    )
                defaults = InputFile.read_ui_json(ui_json).data
            elif isinstance(ui_json, InputFile):
                defaults = ui_json.data

        if not defaults:
            if Path(self._initializer["geoh5"]).exists():
                defaults = self._initializer.copy()
            else:
                warnings.warn(
                    "Geoapps is missing 'FlinFlon.geoh5' file in the assets folder."
                )

        self.defaults.update(defaults)

        self._compute = Button(
            description="Compute",
            button_style="warning",
        )
        self._export_as = Text(
            value="Edges",
            description="Save as:",
            disabled=False,
        )
        self._line_length = IntSlider(
            min=1,
            max=100,
            step=1,
            value=1,
            continuous_update=False,
            description="Line Length",
        )
        self._line_gap = IntSlider(
            min=1,
            max=100,
            step=1,
            value=1,
            continuous_update=False,
            description="Line Gap",
        )
        self._sigma = FloatSlider(
            min=0.0,
            max=10,
            step=0.1,
            value=1.0,
            continuous_update=False,
            description="Sigma",
        )
        self._threshold = IntSlider(
            min=1,
            max=100,
            step=1,
            value=1,
            continuous_update=False,
            description="Threshold",
        )
        self._window_size = IntSlider(
            min=16,
            max=512,
            value=64,
            continuous_update=False,
            description="Window size",
        )
        self.data.observe(self.update_name, names="value")
        self.compute.on_click(self.compute_trigger)
        super().__init__(plot_result=plot_result, **self.defaults)

        # Make changes to trigger warning color
        self.trigger.description = "Export"
        self.trigger.on_click(self.trigger_click)
        self.trigger.button_style = "success"
        self.compute.click()

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, val):
        if not isinstance(val, EdgeParameters):
            raise TypeError("Input parameters must be of type Parameters.")
        self._params = val

    @property
    def compute(self):
        """ToggleButton"""
        return self._compute

    @property
    def export_as(self):
        """Text"""
        return self._export_as

    @property
    def line_length(self):
        """IntSlider"""
        return self._line_length

    @property
    def line_gap(self):
        """IntSlider"""
        return self._line_gap

    @property
    def main(self):
        if self._main is None:
            self._main = VBox(
                [
                    self.project_panel,
                    HBox(
                        [
                            VBox(
                                [
                                    self.data_panel,
                                    self.window_selection,
                                ]
                            ),
                            VBox(
                                [
                                    self.sigma,
                                    self.threshold,
                                    self.line_length,
                                    self.line_gap,
                                    self.window_size,
                                    self.compute,
                                    self.export_as,
                                    self.output_panel,
                                ],
                                layout=Layout(width="50%"),
                            ),
                        ]
                    ),
                ]
            )
        return self._main

    @property
    def sigma(self):
        """FloatSlider"""
        return self._sigma

    @property
    def threshold(self):
        """IntSlider"""
        return self._threshold

    @property
    def window_size(self):
        """IntSlider"""
        return self._window_size

    def is_computational(self, attr):
        """True if app attribute is required for the driver (belongs in params)."""
        out = isinstance(getattr(self, attr), Widget)
        return out & (attr.lstrip("_") in self._initializer)

    def trigger_click(self, _):
        param_dict = self.get_param_dict()
        temp_geoh5 = f"{string_name(param_dict.get('export_as'))}_{time():.0f}.geoh5"
        ws, self.live_link.value = BaseApplication.get_output_workspace(
            self.live_link.value, self.export_directory.selected_path, temp_geoh5
        )

        with fetch_active_workspace(ws) as new_workspace:
            param_dict["geoh5"] = new_workspace
            param_dict["conda_environment"] = "geoapps"

            if self.live_link.value:
                param_dict["monitoring_directory"] = self.monitoring_directory

            with fetch_active_workspace(self.workspace):
                param_dict["objects"], param_dict["data"] = self.get_local_window_data(
                    param_dict["objects"], param_dict["data"], workspace=new_workspace
                )

            new_params = EdgeParameters.build(param_dict)
            new_params.input_file.write_ui_json(
                name=temp_geoh5.replace(".geoh5", ".ui.json")
            )
            driver = EdgesDriver(new_params)
            driver.run()

        if self.live_link.value:
            print("Live link active. Check your ANALYST session for new mesh.")

    def get_local_window_data(
        self, entity: ObjectBase, data: FloatData, workspace: Workspace
    ) -> tuple[ObjectBase, FloatData]:
        """Apply the apps window to object and data."""

        window = {
            "center": [self.window_center_x.value, self.window_center_y.value],
            "size": [self.window_width.value, self.window_height.value],
        }

        indices = filter_xy(
            entity.locations[:, 0],
            entity.locations[:, 1],
            self.resolution.value,
            window=window,
            angle=self.window_azimuth.value,
        )

        entity = entity.copy(parent=workspace, mask=indices, copy_children=False)
        data = data.copy(parent=entity, mask=indices)

        return entity, data

    def update_name(self, _):
        if self.data.value is not None:
            self.export_as.value = self.data.uid_name_map[self.data.value]
        else:
            self.export_as.value = "Edges"

    def compute_trigger(self, _):
        param_dict = self.get_param_dict()
        if param_dict.get("objects", None) is None:
            return

        ws = Workspace()
        param_dict["geoh5"] = ws
        entity, data = self.get_local_window_data(
            param_dict["objects"], param_dict["data"], workspace=ws
        )
        new_params = EdgeParameters.build(param_dict)
        self.refresh.value = False

        canny_grid = EdgesDriver.get_canny_edges(
            entity,
            data,
            new_params.detection,
        )
        vertices, cells = EdgesDriver.get_edges(
            entity,
            canny_grid,
            new_params.detection,
        )
        segments = [vertices[c, :2] for c in cells]
        self.collections = [
            collections.LineCollection(segments, colors="k", linewidths=2)
        ]
        self.refresh.value = True
