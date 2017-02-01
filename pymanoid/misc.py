#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2017 Stephane Caron <stephane.caron@normalesup.org>
#
# This file is part of pymanoid <https://github.com/stephane-caron/pymanoid>.
#
# pymanoid is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pymanoid is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# pymanoid. If not, see <http://www.gnu.org/licenses/>.

from numpy import array, dot, hstack, sqrt

from rotations import quat_slerp


class AvgStdEstimator(object):

    """
    Online estimator for the average and standard deviation of a time series of
    scalar values.
    """

    def __init__(self):
        self.x = 0.
        self.x2 = 0.
        self.n = 0

    def add(self, v):
        """
        Add a new value of the time series.

        Parameters
        ----------
        v : scalar
            New value.
        """
        self.x += v
        self.x2 += v ** 2
        self.n += 1

    @property
    def avg(self):
        """Average of the time series."""
        if self.n < 1:
            return None
        return self.x / self.n

    @property
    def std(self):
        """Standard deviation of the time series."""
        if self.n < 1:
            return None
        elif self.n == 1:
            return 0.
        unbiased = sqrt(self.n * 1. / (self.n - 1))
        return unbiased * sqrt(self.x2 / self.n - self.avg ** 2)


class PointWrap(object):

    """
    An object with a ``p`` array field.

    Parameters
    ----------
    p : list or array
        Point coordinates.
    """

    def __init__(self, p):
        assert len(p) == 3, "Argument is not a point"
        self.p = array(p)


class PoseWrap(object):

    """
    An object with a ``pose`` array field.

    Parameters
    ----------
    p : list or array
        Pose coordinates.
    """

    def __init__(self, pose):
        assert len(pose) == 7, "Argument is not a pose"
        self.pose = array(pose)


def norm(v):
    """Euclidean norm, 2x faster than numpy.linalg.norm on my machine."""
    return sqrt(dot(v, v))


def normalize(v):
    """Normalize a vector. Don't catch ZeroDivisionError on purpose."""
    return v / norm(v)


def plot_polygon(points, alpha=.4, color='g', linestyle='solid', fill=True,
                 linewidth=None):
    """
    Plot a polygon in matplotlib.

    Parameters
    ----------
    points : list of arrays
        List of poitns.
    alpha : scalar, optional
        Transparency value.
    color : string, optional
        Color in matplotlib format.
    linestyle : scalar, optional
        Line style in matplotlib format.
    fill : bool, optional
        When ``True``, fills the area inside the polygon.
    linewidth : scalar, optional
        Line width in matplotlib format.
    """
    from matplotlib.patches import Polygon
    from pylab import axis, gca
    from scipy.spatial import ConvexHull
    if type(points) is list:
        points = array(points)
    ax = gca()
    hull = ConvexHull(points)
    points = points[hull.vertices, :]
    xmin1, xmax1, ymin1, ymax1 = axis()
    xmin2, ymin2 = 1.5 * points.min(axis=0)
    xmax2, ymax2 = 1.5 * points.max(axis=0)
    axis((min(xmin1, xmin2), max(xmax1, xmax2),
          min(ymin1, ymin2), max(ymax1, ymax2)))
    patch = Polygon(
        points, alpha=alpha, color=color, linestyle=linestyle, fill=fill,
        linewidth=linewidth)
    ax.add_patch(patch)


def interpolate_pose_linear(pose0, pose1, t):
    """
    Linear pose interpolation.

    Parameters
    ----------
    pose0 : array
        First pose.
    pose1 : array
        Second pose.
    t : scalar
        Any number between 0 and 1.

    Returns
    pose : array
        Linear interpolation between the first two arguments.
    """
    pos = pose0[4:] + t * (pose1[4:] - pose0[4:])
    quat = quat_slerp(pose0[:4], pose1[:4], t)
    return hstack([quat, pos])


try:
    from minieigen import MatrixXd, VectorXd
except ImportError:
    pass


def array_to_MatrixXd(a):
    A = MatrixXd.Zero(a.shape[0], a.shape[1])
    for i in xrange(a.shape[0]):
        for j in xrange(a.shape[1]):
            A[i, j] = a[i, j]
    return A


def array_to_VectorXd(v):
    V = VectorXd.Zero(v.shape[0])
    for i in xrange(v.shape[0]):
        V[i] = v[i]
    return V


def VectorXd_to_array(V):
    return array([V[i] for i in xrange(V.rows())])
