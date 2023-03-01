"""
Unit test of GlobalXYVisualizer

Author: Shisato Yano
"""

import matplotlib.pyplot as plt
import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../src/visualization")
from global_xy_visualizer import GlobalXYVisualizer


# test instance
vis = GlobalXYVisualizer()


# mock class
class MockObject:
    def __init__(self):
        pass

    def draw(self, a_axes, elems):
        pass


def test_create_instance():
    assert len(vis.objects) == 0
    assert vis.min_lim == -5
    assert vis.max_lim == 5
    assert vis.show_plot == True


def test_draw():
    mock = MockObject()
    vis.add_object(mock)
    assert len(vis.objects) == 1

    vis.not_show_plot()
    assert vis.show_plot == False

    plt.clf()
    vis.draw()
