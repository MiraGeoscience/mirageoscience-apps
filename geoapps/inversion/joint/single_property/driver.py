#  Copyright (c) 2022 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).
from __future__ import annotations

import json

from dask.distributed import Client, LocalCluster, get_client
from geoh5py.data import FilenameData
from SimPEG.objective_function import ComboObjectiveFunction

from geoapps.inversion.driver import InversionDriver
from geoapps.inversion.utils import get_driver_from_json

from .constants import validations
from .params import JointSinglePropertyParams


class JointSinglePropertyDriver(InversionDriver):

    _params_class = JointSinglePropertyParams
    _validations = validations

    def __init__(self, params: JointSinglePropertyParams, warmstart=False):
        super().__init__(params, warmstart=warmstart)

    def initialize(self):

        self.configure_dask()

        # TODO Need to setup/test workers with address
        if self.params.distributed_workers is not None:
            try:
                get_client()
            except ValueError:
                cluster = LocalCluster(processes=False)
                Client(cluster)

        misfits = []
        for label in ["a", "b", "c"]:
            group = getattr(self.params, f"simulation_{label}", None)

            if group is None:
                continue

            input_file = [
                child
                for child in group.children
                if isinstance(child, FilenameData) and "ui.json" in child.name
            ]

            if not input_file:
                raise AttributeError(
                    "Input SimPEGGroup must have a ui.json file attached."
                )
            ui_json = json.loads(input_file[0].values.decode())
            ui_json["geoh5"] = self.workspace
            ui_json["workspace_geoh5"] = self.workspace
            driver = get_driver_from_json(ui_json, warmstart=False)

            misfits.append(driver.data_misfit)

        self._data_misfit = DataMisfit(misfits)

        if self.warmstart and not self.params.forward_only:
            print("Pre-computing sensitivities ...")
            self.inverse_problem.dpred = getattr(
                self.inverse_problem, "get_dpred"
            )(  # pylint: disable=assignment-from-no-return
                self.models.starting, compute_J=True
            )


class DataMisfit:
    """Class handling the data misfit function."""

    def __init__(self, misfits: list):

        objfcts = []
        for misfit in misfits:
            objfcts += misfit.objective_function.objfcts

        self._objective_function = ComboObjectiveFunction(objfcts=objfcts)
        self._sorting = [misfit.sorting for misfit in misfits]

    @property
    def objective_function(self):
        """The Simpeg.data_misfit class"""
        return self._objective_function

    @property
    def sorting(self):
        """List of arrays for sorting of data from tiles."""
        return self._sorting
