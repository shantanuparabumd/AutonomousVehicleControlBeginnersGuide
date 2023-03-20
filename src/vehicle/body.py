"""
body.py

Author: Shisato Yano
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../common")
from transformation import Transformation


class Body:
    """
    Vehicle Body class
    """

    def __init__(self, spec):
        """
        Constructor
        spec: vehicle specification object
        """
        
        self.f_len_m = spec.f_len_m
        self.r_len_m = spec.r_len_m
        self.tread_m = spec.tread_m
        self.f_edge_m = spec.f_edge_m
        self.r_edge_m = spec.r_edge_m
        self.width_m = spec.width_m
        self.color = spec.color
        self.line_w = spec.line_w
        self.line_type = spec.line_type

        self.points = np.array([
            [self.f_edge_m, -self.r_edge_m, -self.r_edge_m, self.f_edge_m, self.f_edge_m],
            [self.width_m, self.width_m, -self.width_m, -self.width_m, self.width_m]
        ])

    def draw(self, axes, pose):
        transformed_points = Transformation.homogeneous_transformation(self.points, pose)
        return axes.plot(transformed_points[0, :], 
                         transformed_points[1, :], 
                         lw=self.line_w, 
                         color=self.color, 
                         ls=self.line_type)
