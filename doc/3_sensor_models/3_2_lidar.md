## 3.2 LiDAR model
In this section, a simple 2D LiDAR model class are implemented for generating a 2D point cloud data. The obstacles in the simulation world can be observed with this LiDAR model.  

### 3.2.1 Sensor parameters
A parameters class, SensorParameters is implemented here. This class has the following parameters for a sensor installation and observation.  

* Longitudinal installation position on a vehicle coordinate system[m]
* Lateral installation position on a vehicle coordinate system[m]
* Yaw angle of installation pose on a vehicle coordinate system[deg]
* Minimum sensing range[m]
* Maximum sensing range[m]
* Resolution of sensing angle[deg]
* Scale of an angle standard deviation
* Rate of a distance standard deviation

SensorParameters class is implemented as follow. [XYArray class](/doc/2_vehicle_model/2_vehicle_model.md) is imported in the class for representing a x-y vector of the position of the sensor. The above parameters can be given to the constructor as arguments.  

[sensor_parameters.py](/src/components/sensors/sensor_parameters.py)  
```python
"""
sensor_parameters.py

Author: Shisato Yano
"""

import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parent) + "/../array")
from xy_array import XYArray


class SensorParameters:
    """
    Parameters class for sensor
    """

    def __init__(self, lon_m=0.0, lat_m=0.0, yaw_deg=0.0, min_m=0.5, max_m=40, reso_deg=2.0,
                 angle_std_scale=0.01, dist_std_rate=0.005):
        """
        Constructor
        lon_m: longitudinal installation position on vehicle coordinate system[m]
        lat_m: lateral installation position on vehicle coordinate system[m]
        yaw_deg: yaw angle of installation position on vehicle coordinate system[deg]
        min_m: minimum sensing range[m]
        max_m: maximum sensing range[m]
        reso_deg: resolution of sensing angle[deg]
        angle_std_scale: scale of angle's standard deviation
        dist_std_rate: rate of distance's standard deviation
        """
        
        self.INST_LON_M = lon_m
        self.INST_LAT_M = lat_m
        self.INST_YAW_RAD = np.deg2rad(yaw_deg)

        self.MIN_RANGE_M = min_m
        self.MAX_RANGE_M = max_m

        self.RESO_RAD = np.deg2rad(reso_deg)

        self.ANGLE_STD_SCALE = angle_std_scale
        self.DIST_STD_RATE = dist_std_rate

        self.inst_pos_array = XYArray(np.array([[self.INST_LON_M], [self.INST_LAT_M]]))
        self.global_x_m = None
        self.global_y_m = None
```

And then, some member methods, calculate_global_pos, get_global_x_m, get_global_y_m and  draw_pos are implemented. calculate_global_pos method is used for transforming the position and pose of the sensor from the vehicle coordinate system to the global coordinate system based on the state of the vehicle.  
```python
    def calculate_global_pos(self, state):
        """
        Function to calculate sensor's installation position on global coordinate system
        state: vehicle's state object
        """

        pose = state.x_y_yaw()
        transformed_array = self.inst_pos_array.homogeneous_transformation(pose[0, 0], pose[1, 0], pose[2, 0])
        
        self.global_x_m = transformed_array.get_x_data()
        self.global_y_m = transformed_array.get_y_data()
```

get_global_x_m and get_global_y_m are used for getting the global position of the sensor.  
```python
    def get_global_x_m(self):
        """
        Getter of sensor's x installation position on global coordinate system
        """

        return self.global_x_m[0]
    
    def get_global_y_m(self):
        """
        Getter of sensor's y installation position on global coordinate system
        """

        return self.global_y_m[0]
```

draw_pos is used for visualizing the position of the sensor in the simulation world. In this method, the position of the sensor is transformed into the global position and visualized.  
```python
    def draw_pos(self, axes, elems, state):
        """
        Function to draw sensor's installation position on vehicle
        axes: axes object of figure
        elems: list of plot object
        state: vehicle state object
        """

        self.calculate_global_pos(state)
        pos_plot, = axes.plot(self.global_x_m, self.global_y_m, marker='.', color='b')
        elems.append(pos_plot)
```

### 3.2.2 Homogeneous transformation matrix
For transforming the generated point cloud, some utility methods of transformation matrix. These methods can process homogeneous 2D transformation and rotation.  
[matrix_lib.py](/src/components/common/matrix_lib.py)  
```python
"""
matrix_lib.py

Author: Shisato Yano
"""

import numpy as np
from math import sin, cos


def hom_mat_33(x, y, yaw):
    """
    Homogeneous transformation matrix 3x3
    x: x direction translation[m]
    y: y direction translation[m]
    yaw: yaw direction rotation[rad]
    """

    cos_yaw, sin_yaw = cos(yaw), sin(yaw)

    return np.array([[cos_yaw, -sin_yaw, x],
                     [sin_yaw, cos_yaw, y],
                     [0.0, 0.0, 1.0]])


def rot_mat_22(yaw):
    cos_yaw, sin_yaw = cos(yaw), sin(yaw)

    return np.array([[cos_yaw, -sin_yaw],
                     [sin_yaw, cos_yaw]])
```

### 3.2.3 Scan point
ScanPoint class is implemented to represent a scan point in a point cloud from LiDAR. [XYArray class](/doc/2_vehicle_model/2_vehicle_model.md) is imported in the class for representing a x-y vector of the position of the scan point. The scan point object has the following data.  

* Distance from the LiDAR to the scan point[m]
* Horizontal angle from the LiDAR to the scan point[rad]
* X-Y position array of the scan point[m]
* Trasformed x coordinate of the scan point on a specific coordinate system
* Trasformed y coordinate of the scan point on a specific coordinate system

The constructor of ScanPoint class is implemented as follow. A distance, horizontal angle, x coordinate and y coordinate are given as arguments.  
[scan_point.py](/src/components/sensors/lidar/scan_point.py)  
```python
"""
scan_point.py

Author: Shisato Yano
"""

import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parent) + "/../../array")
sys.path.append(str(Path(__file__).absolute().parent) + "/../../common")
from xy_array import XYArray
from matrix_lib import hom_mat_33


class ScanPoint:
    """
    Scan point of sensor class includes each sensing data
    """
    
    def __init__(self, distance_m, angle_rad, x_m, y_m):
        """
        Constructor
        distance_m: sensed distance data[m]
        angle_rad: sensed angle data[rad]
        x_m: sensed point's x coordinate data[m]
        y_m: sensed point's y coordinate data[m]
        """
        
        self.distance_m = distance_m
        self.angle_rad = angle_rad
        self.point_array = XYArray(np.array([[x_m], [y_m]]))
        self.transformed_x = None
        self.transformed_y = None
```

Then, some member methods for accessing or visualizing the data. The getter methods for a dimension of x-y array, distance and x-y array of point are implemented as follow.  
```python
    def get_dimension(self):
        """
        Return point's x-y array data's dimension value
        """

        return self.point_array.get_dimension()
    
    def get_distance_m(self):
        """
        Return point's distance data[m]
        """
        
        return self.distance_m
    
    def get_point_array(self):
        """
        Return point's x-y array data
        Type is ndarray object
        """

        return self.point_array.get_data()
```