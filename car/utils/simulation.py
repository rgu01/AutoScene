import os
import warnings
import subprocess
import numpy as np
from commonroad.geometry.shape import Rectangle
from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.common.file_writer import CommonRoadFileWriter
from commonroad.common.file_writer import OverwriteExistingFile
from commonroad.planning.planning_problem import PlanningProblemSet
from commonroad.scenario.scenario import Scenario, Tag
from commonroad.visualization.mp_renderer import MPRenderer, MPDrawParams
from commonroad.scenario.obstacle import DynamicObstacle, ObstacleType
from commonroad.scenario.state import CustomState, InitialState
from commonroad.scenario.trajectory import Trajectory
from commonroad.prediction.prediction import TrajectoryPrediction
warnings.filterwarnings('ignore')

class Simulation:
    def __init__(self, scenario:Scenario):
        self.scenario = scenario
        try:
            subprocess.run(["bash", "car/shield/simulate_test_vehicle.sh"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.test_vehicle_trajectory = self.convert(self.read_sample_log("sampling.log"))
            subprocess.run(["bash", "car/shield/simulate_ego_vehicle.sh"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.ego_vehicle_trajectory = self.convert(self.read_sample_log("sampling.log"))
        except subprocess.CalledProcessError as e:
            print("Error:\n", e.stderr)

    def read_sample_log(self, path):
        #print("Current working directory:", os.getcwd())
        with open(path, 'r') as f:
            data = f.read().splitlines()
        data = [list(map(float, line.split(' '))) for line in data]
        return data

    # data has 7 elements: time, position on X, position on Y, velocity on X, velocity on Y, acceleration on X, acceleration on Y
    def convert(self, data):
        # new data has 6 elements: time, position on X, position on Y, heading, velocity, acceleration
        new_data = []
        for row in data:
            t, x, y, vel_x, vel_y, acc_x, acc_y = row

            heading = np.arctan2(vel_y, vel_x)
            velocity = np.sqrt(vel_x**2 + vel_y**2)
            acceleration = np.sqrt(acc_x**2 + acc_y**2)

            new_row = [t, x, y, heading, velocity, acceleration]
            new_data.append(new_row)

        return new_data

    def make_dynamic_obstacle(self, obstacle_id, data, type:ObstacleType, w=1, l=4.5):
        t, x, y, orientation, velocity, acceleration = data[0]
        initial_state = CustomState(
            position=np.array([x, y]),
            velocity=velocity,
            orientation=orientation,
            time_step=0
        ).convert_state_to_state(InitialState())

        state_list = []
        for row in data[1:]:
            t, x, y, orientation, velocity, acceleration = row
            state = CustomState(
                position=np.array([x, y]),
                velocity=velocity,
                orientation=orientation,
                acceleration=acceleration,
                time_step=int(t)
            )
            state_list.append(state)

        trajectory = Trajectory(1, state_list)
        shape = Rectangle(width=w, length=l)
        prediction = TrajectoryPrediction(trajectory, shape)

        obstacle = DynamicObstacle(
            obstacle_id, type, shape, initial_state, prediction
        )
        return obstacle

    def create_animation(self, time):
        rnd = MPRenderer()
        dp = MPDrawParams()
        dp.time_end = time
        dp.dynamic_obstacle.draw_icon = True
        dp.dynamic_obstacle.draw_shape = True
        rnd.create_video([self.scenario, ], f"car/animation/{str(self.scenario.scenario_id)}_scenario.gif", draw_params=dp)

    def generate(self, clear=False):
        if(clear):
            self.scenario.remove_obstacle(self.scenario.dynamic_obstacles)

        test_vehicle = self.make_dynamic_obstacle(self.scenario.generate_object_id(), self.test_vehicle_trajectory, ObstacleType.CAR)
        self.scenario.add_objects(test_vehicle)
        ego_vehicle = self.make_dynamic_obstacle(self.scenario.generate_object_id(), self.ego_vehicle_trajectory, ObstacleType.TRUCK)
        self.scenario.add_objects(ego_vehicle)

        self.create_animation(len(self.ego_vehicle_trajectory))