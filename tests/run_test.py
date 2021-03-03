#  Copyright (c) 2021 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

from shutil import copyfile

import pytest

from geoapps.export import Export
from geoapps.inversion import InversionApp
from geoapps.processing import (
    Calculator,
    Clustering,
    ContourValues,
    CoordinateTransformation,
    DataInterpolation,
    EdgeDetectionApp,
    PeakFinder,
    Surface2D,
)

project = "Project_work.geoh5"


def test_calculator():
    copyfile(r"..\assets\FlinFlon.geoh5", project)
    app = Calculator(h5file=project)
    app.trigger.click()


def test_coordinate_transformation():
    app = CoordinateTransformation(h5file=project)
    app.trigger.click()


def test_contour_values():
    app = ContourValues(h5file=project)
    app.trigger.click()


def test_create_surface():
    app = Surface2D(h5file=project)
    app.trigger.click()


def test_clustering():
    app = Clustering(h5file=project)
    app.trigger.click()


def test_data_interpolation():
    app = DataInterpolation(h5file=project)
    app.trigger.click()


def test_edge_detection():
    app = EdgeDetectionApp(h5file=project)
    app.trigger.click()


def test_export():
    app = Export(h5file=project)
    app.trigger.click()


def test_inversion():
    app = InversionApp(
        h5file=project,
        inversion_parameters={"max_iterations": 1},
    )
    app.write.value = True
    app.run.value = True


def test_peak_finder():
    app = PeakFinder(h5file=project)
    app.run_all.click()
    app.trigger.click()
