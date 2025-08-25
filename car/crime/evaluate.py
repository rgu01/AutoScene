from commonroad_crime.data_structure.configuration import CriMeConfiguration
from commonroad_crime.data_structure.crime_interface import CriMeInterface
from commonroad_crime.data_structure.crime_interface import CriMeInterface
from commonroad_crime.measure import (HW, TTC, TTR, TTCStar, ALongReq, LongJ, BTN, P_MC, PF)
import os

def init_config(scenario_id):
    path_root_abs = os.path.normpath(os.path.join(os.path.dirname(__file__), "../..")) + "/car"
    config = CriMeConfiguration.load(f"car/scenarios/config_files/{scenario_id}.yaml", scenario_id)
    config.general.path_root_abs = path_root_abs
    config.general.path_scenarios = path_root_abs + "/scenarios/"
    config.general.path_scenarios_batch = path_root_abs + "/scenarios/batch/"
    config.general.path_output_abs = path_root_abs + "/crime/output/"
    config.general.path_logs = path_root_abs + "/crime/output/logs/"
    config.general.path_icons = path_root_abs + "/crime/docs/icons/"
    config.update()
    config.print_configuration_summary()

    return config


def measure_single_criticality(scenario_id, metrics="TTCStar"):
    config = init_config(scenario_id)
    if(metrics == "TTCStar"):
        evaluator = TTCStar(config)
    time_step = 0
    other_veh_id = 30627
    evaluator.compute(time_step, other_veh_id)

def measure_multiple_criticality(scenario_id, ts_start=0, ts_end=10):
    config = init_config(scenario_id)
    crime_interface = CriMeInterface(config)
    crime_interface.evaluate_scene([HW, TTC, TTR, ALongReq, LongJ, BTN, P_MC, PF],)
    crime_interface.evaluate_scenario([HW, TTC, TTR, ALongReq, LongJ, BTN, P_MC, PF], ts_start, ts_end)