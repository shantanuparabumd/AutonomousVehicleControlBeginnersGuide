"""
lqr_controller.py

Author: Shisato Yano
"""

#import path setting
import sys
from pathlib import Path
from math import sin, cos, atan2

abs_dir_path = str(Path(__file__).absolute().parent)
relative_path = "/../../../components/"

sys.path.append(abs_dir_path + relative_path + "control/speed_profile")

#import component modules
from trapezoidal_speed_profile import TrapezoidalSpeedProfile


class LqrController:
    """
    Controller class by LQR(Linear Quadratic Regulator) algorithm
    """

    def __init__(self, spec, course=None):
        """
        Constructor
        spec: VehicleSpecification object
        course: Course data and logic object
        """

        self.WHEEL_BASE_M = spec.wheel_base_m
        self.MAX_ACCEL_MPS2 = spec.max_accel_mps2

        self.course = course
        self.target_course_index = 0
        self.target_accel_mps2 = 0.0
        self.target_speed_mps = 0.0
        self.target_yaw_rate_rps = 0.0
        self.target_steer_rad = 0.0
        self.elapsed_time_sec = 0.0

        if self.course:
            max_spd_mps = self.course.max_speed_mps()
            distance_m = self.course.distance_m()
        else:
            max_spd_mps = 1e-100
            distance_m = 1e-100
        
        self.spd_prf = TrapezoidalSpeedProfile(max_spd_mps, self.MAX_ACCEL_MPS2, distance_m)

    def _calculate_target_course_index(self, state):
        """
        Private function to calculate target point's index on course
        state: Vehicle's state object
        """
        
        nearest_index = self.course.search_nearest_point_index(state)
        self.target_course_index = nearest_index

    def _calculate_tracking_error(self, state):
        """
        Private function to calculate tracking error against target point on the course
        state: Vehicle's state object
        """

        error_lon_m, error_lat_m, error_yaw_rad = self.course.calculate_lonlat_error(state, self.target_course_index)
        return error_lon_m, error_lat_m, error_yaw_rad

    def _decide_target_speed_mps(self, time_s):
        """
        Private function to decide target speed[m/s]
        time_s: interval time[sec]
        """

        self.target_speed_mps = self.spd_prf.decide_target_speed_mps(self.elapsed_time_sec, time_s)

    def _calculate_control_input(self, state, error_lat_m, error_yaw_rad, time_s):
        """
        Private function to calculate yaw rate input
        state: Vehicle's state object
        error_lat_m: Lateral error against reference course[m]
        error_yaw_rad: Yaw angle error against reference course[rad]
        time_s: Simulation interval time[sec]
        """

        curr_spd = state.get_speed_mps()
        trgt_curv = self.course.point_curvature(self.target_course_index)

    def update(self, state, time_s):
        """
        Function to update data for path tracking
        state: Vehicle's state object
        time_s: Simulation interval time[sec]
        """

        if not self.course: return

        self._calculate_target_course_index(state)

        self._decide_target_speed_mps(time_s)

        _, error_lat_m, error_yaw_rad = self._calculate_tracking_error(state)

        self._calculate_control_input(state, error_lat_m, error_yaw_rad, time_s)

        self.elapsed_time_sec += time_s

    def draw(self, axes, elems):
        """
        Function to draw target point on course
        axes: Axes object of figure
        elems: plot object's list
        """

        pass
