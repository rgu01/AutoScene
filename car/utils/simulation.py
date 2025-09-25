import os
import warnings
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

def read_sample_log(path):
    print("Current working directory:", os.getcwd())
    with open(path, 'r') as f:
        data = f.read().splitlines()
    data = [list(map(float, line.split(' '))) for line in data]
    return data

# data has 7 elements: time, position on X, position on Y, velocity on X, velocity on Y, acceleration on X, acceleration on Y
def convert(data):
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

def make_dynamic_obstacle(obstacle_id, data, w=1, l=4.5):
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
        obstacle_id, ObstacleType.UNKNOWN, shape, initial_state, prediction
    )
    return obstacle

def create_animation(scenario, planning_problem_set, time):
    rnd = MPRenderer()
    dp = MPDrawParams()
    dp.time_end = time
    dp.dynamic_obstacle.draw_icon = True
    dp.dynamic_obstacle.draw_shape = True
    rnd.create_video([scenario, planning_problem_set], f"car/animation/{str(scenario.scenario_id)}_scenario.gif", draw_params=dp)


def save_scenario(scenario: Scenario, planning_problem_set: PlanningProblemSet, filename):
    author = 'Max Mustermann'
    affiliation = 'Technical University of Munich, Germany'
    source = ''
    tags = {Tag.CRITICAL, Tag.INTERSTATE}
    # write new scenario
    fw = CommonRoadFileWriter(scenario, planning_problem_set, author, affiliation, source, tags)
    fw.write_to_file(filename, OverwriteExistingFile.ALWAYS)

def generate(SCENARIO_PATH, SAMPLING_LOG_PATH, save=False):
    scenario, planning_problem_set = CommonRoadFileReader(SCENARIO_PATH).open()
    # Read sample log
    sample = convert(read_sample_log(SAMPLING_LOG_PATH))
    #sample = read_sample_log(SAMPLING_LOG_PATH)
    new_vehicle = make_dynamic_obstacle(scenario.generate_object_id(), sample)
    scenario.add_objects(new_vehicle)

    if(save):
        base, ext = os.path.splitext(SCENARIO_PATH)
        new_scenario_path = f"{base}-scenario{ext}"
        save_scenario(scenario, planning_problem_set, new_scenario_path)

    create_animation(scenario, planning_problem_set, len(sample))