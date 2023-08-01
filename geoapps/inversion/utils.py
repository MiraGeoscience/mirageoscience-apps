#  Copyright (c) 2023 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

from __future__ import annotations

import warnings

import numpy as np
from discretize import TreeMesh
from geoh5py import Workspace
from geoh5py.data import Data
from scipy.spatial import ConvexHull, Delaunay, cKDTree, qhull
from SimPEG.survey import BaseSurvey
from SimPEG.utils import mkvc

from geoapps.shared_utils.utils import filter_xy, get_locations
from geoapps.utils.surveys import get_unique_locations


def calculate_2D_trend(
    points: np.ndarray, values: np.ndarray, order: int = 0, method: str = "all"
):
    """
    detrend2D(points, values, order=0, method='all')

    Function to remove a trend from 2D scatter points with values

    Parameters:
    ----------

    points: array or floats, shape(*, 2)
        Coordinates of input points

    values: array of floats, shape(*,)
        Values to be de-trended

    order: Order of the polynomial to be used

    method: str
        Method to be used for the detrending
            "all": USe all points
            "perimeter": Only use points on the convex hull


    Returns
    -------

    trend: array of floats, shape(*,)
        Calculated trend

    coefficients: array of floats, shape(order+1)
        Coefficients for the polynomial describing the trend

        trend = c[0] + points[:, 0] * c[1] +  points[:, 1] * c[2]
    """
    if not isinstance(order, int) or order < 0:
        raise ValueError(
            "Polynomial 'order' should be an integer > 0. "
            f"Value of {order} provided."
        )

    ind_nan = ~np.isnan(values)
    loc_xy = points[ind_nan, :]
    values = values[ind_nan]

    if method == "perimeter":
        hull = ConvexHull(loc_xy[:, :2])
        # Extract only those points that make the ConvexHull
        loc_xy = loc_xy[hull.vertices, :2]
        values = values[hull.vertices]
    elif not method == "all":
        raise ValueError(
            "'method' must be either 'all', or 'perimeter'. " f"Value {method} provided"
        )

    # Compute center of mass
    center_x = np.sum(loc_xy[:, 0] * np.abs(values)) / np.sum(np.abs(values))
    center_y = np.sum(loc_xy[:, 1] * np.abs(values)) / np.sum(np.abs(values))

    polynomial = []
    xx, yy = np.triu_indices(order + 1)
    for x, y in zip(xx, yy):
        polynomial.append(
            (loc_xy[:, 0] - center_x) ** float(x)
            * (loc_xy[:, 1] - center_y) ** float(y - x)
        )
    polynomial = np.vstack(polynomial).T

    if polynomial.shape[0] <= polynomial.shape[1]:
        raise ValueError(
            "The number of input values must be greater than the number of coefficients in the polynomial. "
            f"Provided {polynomial.shape[0]} values for a {order}th order polynomial with {polynomial.shape[1]} coefficients."
        )

    params, _, _, _ = np.linalg.lstsq(polynomial, values, rcond=None)
    data_trend = np.zeros(points.shape[0])
    for count, (x, y) in enumerate(zip(xx, yy)):
        data_trend += (
            params[count]
            * (points[:, 0] - center_x) ** float(x)
            * (points[:, 1] - center_y) ** float(y - x)
        )
    print(
        f"Removed {order}th order polynomial trend with mean: {np.mean(data_trend):.6g}"
    )
    return data_trend, params


def create_nested_mesh(
    survey: BaseSurvey,
    base_mesh: TreeMesh,
    method: str = "padding_cells",
    padding_cells: int = 8,
    minimum_level: int = 3,
    finalize: bool = True,
):
    """
    Create a nested mesh with the same extent as the input global mesh.
    Refinement levels are preserved only around the input locations (local survey).

    Parameters
    ----------

    locations: Array of coordinates for the local survey shape(*, 3).
    base_mesh: Input global TreeMesh object.
    method: Refinement of cells from the base mesh determined by from either
        'convex_hull': Cells that fall inside a 2D Delaunay triangulation of the input locations.
        'padding_cells':  Cells inside concentric shells made of 'padding_cells'
    padding_cells: Used for 'method'= 'padding_cells'. Number of cells in each concentric shell.
    minimum_level: Minimum octree level to preserve everywhere outside the local survey area.
    finalize: Return a finalized local treemesh.
    """
    locations = get_unique_locations(survey)
    nested_mesh = TreeMesh(
        [base_mesh.h[0], base_mesh.h[1], base_mesh.h[2]], x0=base_mesh.x0
    )
    base_level = base_mesh.max_level - minimum_level
    base_refinement = base_mesh.cell_levels_by_index(np.arange(base_mesh.nC))
    base_refinement[base_refinement > base_level] = base_level
    nested_mesh.insert_cells(
        base_mesh.gridCC,
        base_refinement,
        finalize=False,
    )

    if method == "convex_hull":
        # Find cells inside the data extant
        try:
            tri2D = Delaunay(locations[:, :2])
            indices = tri2D.find_simplex(base_mesh.gridCC[:, :2]) != -1
            return nested_mesh.insert_cells(
                base_mesh.gridCC[indices, :],
                base_mesh.cell_levels_by_index(np.where(indices)[0]),
                finalize=finalize,
            )
        except qhull.QhullError:
            warnings.warn(
                "qhull failed to triangulate. Defaulting to 'padding_cells' method."
            )
    elif method != "padding_cells":
        raise ValueError(
            "Input 'method' must be one of 'convex_hull' or 'padding_cells'."
        )

    base_cell = np.min([base_mesh.h[0][0], base_mesh.h[1][0]])
    tree = cKDTree(locations[:, :2])
    center = np.mean(base_mesh.gridCC[:, :2], axis=0)
    stretched_cc = (
        (base_mesh.gridCC[:, :2] - center)
        * (base_cell / np.r_[base_mesh.h[0][0], base_mesh.h[1][0]])
    ) + center
    rad, _ = tree.query(stretched_cc)
    pad_distance = 0.0
    for ii in range(minimum_level):
        pad_distance += base_cell * 2**ii * padding_cells
        indices = np.where(rad < pad_distance)[0]
        # indices = np.where(tri2D.find_simplex(base_mesh.gridCC[:, :2]) != -1)[0]
        levels = base_mesh.cell_levels_by_index(indices)
        levels[levels > (base_mesh.max_level - ii)] = base_mesh.max_level - ii
        nested_mesh.insert_cells(
            base_mesh.gridCC[indices, :],
            levels,
            finalize=False,
        )

    if finalize:
        nested_mesh.finalize()

    return nested_mesh


def window_data(
    data_object,
    components,
    data_dict,
    workspace,
    window_azimuth,
    window_center_x,
    window_center_y,
    window_width,
    window_height,
    mesh,
    resolution,
) -> (np.ndarray, dict, np.ndarray):
    """
    Get locations and mask for detrending data.

    :param workspace: New workspace.
    :param param_dict: Dictionary of params to give to _run_params.

    :return locations: Data object locations.
    :return mask: Mask for windowing data.
    """
    # Get locations
    locations = get_locations(workspace, data_object)
    # Get window
    window = {
        "azimuth": window_azimuth,
        "center_x": window_center_x,
        "center_y": window_center_y,
        "width": window_width,
        "height": window_height,
        "center": [
            window_center_x,
            window_center_y,
        ],
        "size": [window_width, window_height],
    }
    # Get angle
    angle = None
    if mesh is not None:
        if hasattr(mesh, "rotation"):
            angle = -1 * mesh.rotation
    # Get mask
    mask = filter_xy(
        locations[:, 0],
        locations[:, 1],
        window=window,
        angle=angle,
        distance=resolution,
    )

    # Apply mask to data object
    west = window["center_x"] - window["width"] / 2
    east = window["center_x"] + window["width"] / 2
    south = window["center_y"] - window["height"] / 2
    north = window["center_y"] + window["height"] / 2

    new_data_object = data_object.copy_from_extent(
        np.array([[west, south], [east, north]]),
        name=data_object.name + "_processed",
        # rotation=0.0,
    )

    # Update data dict
    for comp in components:
        data_dict[comp + "_channel"]["values"] = new_data_object.get_entity(
            data_dict[comp + "_channel"]["name"]
        )[0].values
        if comp + "_uncertainty" in data_dict:
            data_dict[comp + "_uncertainty"] = new_data_object.get_entity(
                data_dict[comp + "_uncertainty"]["name"]
            )[0].values

    # Get new locations
    if hasattr(new_data_object, "centroids"):
        locations = new_data_object.centroids
    elif hasattr(new_data_object, "vertices"):
        locations = new_data_object.vertices

    return new_data_object, data_dict, locations


def detrend_data(
    detrend_type,
    detrend_order,
    components,
    data_dict,
    locations,
):
    """
    Detrend data and update data values in param_dict.

    :param param_dict: Dictionary of params to create self._run_params.
    :param workspace: Output workspace.
    :param detrend_order: Order of the polynomial to be used.
    :param detrend_type: Method to be used for the detrending.
        "all": Use all points.
        "perimeter": Only use points on the convex hull .

    :return: Updated param_dict with updated data.
    """
    if detrend_type == "none" or detrend_type is None or detrend_order is None:
        return data_dict

    for comp in components:
        data = data_dict[comp + "_channel"]
        # Get data trend
        values = data["values"]
        data_trend, _ = calculate_2D_trend(
            locations,
            values,
            detrend_order,
            detrend_type,
        )
        # Update data values and add to object
        data["values"] -= data_trend
    return data_dict


def set_infinity_uncertainties(
    ignore_values,
    forward_only,
    components,
    data_dict,
) -> np.ndarray:
    """
    Use ignore_value ignore_type to set uncertainties to infinity.
    """
    ignore_value, ignore_type = parse_ignore_values(ignore_values, forward_only)

    for comp in components:
        if comp + "_uncertainty" not in data_dict:
            continue
        data = data_dict[comp + "_channel"]["values"]
        uncertainty = data_dict[comp + "_uncertainty"]["values"]
        uncertainty[np.isnan(data)] = np.inf

        if ignore_value is None:
            continue
        elif ignore_type == "<":
            uncertainty[data <= ignore_value] = np.inf
        elif ignore_type == ">":
            uncertainty[data >= ignore_value] = np.inf
        elif ignore_type == "=":
            uncertainty[data == ignore_value] = np.inf
        else:
            msg = f"Unrecognized ignore type: {ignore_type}."
            raise (ValueError(msg))

        data_dict[comp + "_uncertainty"]["values"] = uncertainty

    return data_dict


def parse_ignore_values(ignore_values, forward_only) -> tuple[float, str]:
    """
    Returns an ignore value and type ('<', '>', or '=') from params data.
    """
    if forward_only:
        return None, None

    if ignore_values is None:
        return None, None
    ignore_type = [k for k in ignore_values if k in ["<", ">"]]
    ignore_type = "=" if not ignore_type else ignore_type[0]
    if ignore_type in ["<", ">"]:
        ignore_value = float(ignore_values.split(ignore_type)[1])
    else:
        try:
            ignore_value = float(ignore_values)
        except ValueError:
            return None, None

    return ignore_value, ignore_type


def get_data_dict(param_dict):
    """ """
    # Get components
    components = []
    data_dict = {}
    for key, value in param_dict.items():
        if key.endswith("_channel_bool") and value:
            comp = key.replace("_channel_bool", "")
            components.append(comp)
            data_dict[comp + "_channel"] = {
                "name": param_dict[comp + "_channel"].name,
            }
            if isinstance(param_dict[comp + "_uncertainty"], Data):
                data_dict[comp + "_uncertainty"] = {
                    "name": param_dict[comp + "_uncertainty"].name,
                }

    return components, data_dict


def preprocess_data(
    workspace: Workspace,
    param_dict,
    resolution,
    window_center_x,
    window_center_y,
    window_width,
    window_height,
    window_azimuth=None,
    ignore_values=None,
    detrend_type=None,
    detrend_order=None,
):
    """ """
    data_object = param_dict["data_object"]
    components, data_dict = get_data_dict(param_dict)

    # Windowing
    new_data_object, data_dict, locations = window_data(
        data_object,
        components,
        data_dict,
        workspace,
        window_azimuth,
        window_center_x,
        window_center_y,
        window_width,
        window_height,
        param_dict["mesh"],
        resolution,
    )

    # Ignore values
    if ignore_values is not None:
        data_dict = set_infinity_uncertainties(
            ignore_values,
            param_dict["forward_only"],
            components,
            data_dict,
        )
    # Detrending
    if detrend_type is not None and detrend_order is not None:
        data_dict = detrend_data(
            detrend_type,
            detrend_order,
            components,
            data_dict,
            locations,
        )

    # Add processed data to data object
    update_dict = {}
    update_dict["data_object"] = new_data_object.uid
    for comp in components:
        for key in [comp + "_channel", comp + "_uncertainty"]:
            if key not in data_dict.keys():
                continue
            data = data_dict[key]
            if key in data_dict.keys():
                print(key)
                update_dict[key] = new_data_object.get_entity(data["name"])[0].uid
                print(update_dict[key])

    return update_dict


def tile_locations(
    locations,
    n_tiles,
    minimize=True,
    method="kmeans",
    bounding_box=False,
    count=False,
    unique_id=False,
):
    """
    Function to tile a survey points into smaller square subsets of points

    :param numpy.ndarray locations: n x 2 array of locations [x,y]
    :param integer n_tiles: number of tiles (for 'cluster'), or number of
        refinement steps ('other')
    :param Bool minimize: shrink tile sizes to minimum
    :param string method: set to 'kmeans' to use better quality clustering, or anything
        else to use more memory efficient method for large problems
    :param bounding_box: bool [False]
        Return the SW and NE corners of each tile.
    :param count: bool [False]
        Return the number of locations in each tile.
    :param unique_id: bool [False]
        Return the unique identifiers of all tiles.

    RETURNS:
    :param list: Return a list of arrays with the for the SW and NE
                        limits of each tiles
    :param integer binCount: Number of points in each tile
    :param list labels: Cluster index of each point n=0:(nTargetTiles-1)
    :param numpy.array tile_numbers: Vector of tile numbers for each count in binCount

    NOTE: All X Y and xy products are legacy now values, and are only used
    for plotting functions. They are not used in any calculations and could
    be dropped from the return calls in future versions.


    """

    if method == "kmeans":
        # Best for smaller problems

        np.random.seed(0)
        # Cluster
        # TODO turn off filter once sklearn has dealt with the issue causeing the warning
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            from sklearn.cluster import KMeans

            cluster = KMeans(n_clusters=n_tiles, n_init="auto")
            cluster.fit_predict(locations[:, :2])

        labels = cluster.labels_

        # nData in each tile
        binCount = np.zeros(int(n_tiles))

        # x and y limits on each tile
        X1 = np.zeros_like(binCount)
        X2 = np.zeros_like(binCount)
        Y1 = np.zeros_like(binCount)
        Y2 = np.zeros_like(binCount)

        for ii in range(int(n_tiles)):
            mask = cluster.labels_ == ii
            X1[ii] = locations[mask, 0].min()
            X2[ii] = locations[mask, 0].max()
            Y1[ii] = locations[mask, 1].min()
            Y2[ii] = locations[mask, 1].max()
            binCount[ii] = mask.sum()

        xy1 = np.c_[X1[binCount > 0], Y1[binCount > 0]]
        xy2 = np.c_[X2[binCount > 0], Y2[binCount > 0]]

        # Get the tile numbers that exist, for compatibility with the next method
        tile_id = np.unique(cluster.labels_)

    else:
        # Works on larger problems
        # Initialize variables
        # Test each refinement level for maximum space coverage
        nTx = 1
        nTy = 1
        for ii in range(int(n_tiles + 1)):
            nTx += 1
            nTy += 1

            testx = np.percentile(locations[:, 0], np.arange(0, 100, 100 / nTx))
            testy = np.percentile(locations[:, 1], np.arange(0, 100, 100 / nTy))

            # if ii > 0:
            dx = testx[:-1] - testx[1:]
            dy = testy[:-1] - testy[1:]

            if np.mean(dx) > np.mean(dy):
                nTx -= 1
            else:
                nTy -= 1

            print(nTx, nTy)
        tilex = np.percentile(locations[:, 0], np.arange(0, 100, 100 / nTx))
        tiley = np.percentile(locations[:, 1], np.arange(0, 100, 100 / nTy))

        X1, Y1 = np.meshgrid(tilex, tiley)
        X2, Y2 = np.meshgrid(
            np.r_[tilex[1:], locations[:, 0].max()],
            np.r_[tiley[1:], locations[:, 1].max()],
        )

        # Plot data and tiles
        X1, Y1, X2, Y2 = mkvc(X1), mkvc(Y1), mkvc(X2), mkvc(Y2)
        binCount = np.zeros_like(X1)
        labels = np.zeros_like(locations[:, 0])
        for ii in range(X1.shape[0]):
            mask = (
                (locations[:, 0] >= X1[ii])
                * (locations[:, 0] <= X2[ii])
                * (locations[:, 1] >= Y1[ii])
                * (locations[:, 1] <= Y2[ii])
            ) == 1

            # Re-adjust the window size for tight fit
            if minimize:
                if mask.sum():
                    X1[ii], X2[ii] = (
                        locations[:, 0][mask].min(),
                        locations[:, 0][mask].max(),
                    )
                    Y1[ii], Y2[ii] = (
                        locations[:, 1][mask].min(),
                        locations[:, 1][mask].max(),
                    )

            labels[mask] = ii
            binCount[ii] = mask.sum()

        xy1 = np.c_[X1[binCount > 0], Y1[binCount > 0]]
        xy2 = np.c_[X2[binCount > 0], Y2[binCount > 0]]

        # Get the tile numbers that exist
        # Since some tiles may have 0 data locations, and are removed by
        # [binCount > 0], the tile numbers are no longer contiguous 0:nTiles
        tile_id = np.unique(labels)

    tiles = []
    for tid in tile_id.tolist():
        tiles += [np.where(labels == tid)[0]]

    out = [tiles]

    if bounding_box:
        out.append([xy1, xy2])

    if count:
        out.append(binCount[binCount > 0])

    if unique_id:
        out.append(tile_id)

    if len(out) == 1:
        return out[0]
    return tuple(out)
