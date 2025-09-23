from car.utils.tiga_strategy import TiGaStrategy
from car.utils.config import Configuration
from car.utils.c_builder import C_Builder
from commonroad.common.file_reader import CommonRoadFileReader

class LogicScenario(TiGaStrategy):
    def update_paras(self, config):
        config.ego_vehicle.ego_id = 3
        return config

if __name__ == '__main__':
    scenario_id = "DEU_A9-2_1_T-1"
    logic_scenario_config = Configuration(scenario_id, "logic")
    logic_scenario_path = f"car/shield/{scenario_id}_{logic_scenario_config.logic_params.type}.json"
    cutin = LogicScenario(logic_scenario_path)
    #cutin.update_paras(logic_scenario_config)
    #print(logic_scenario_config.ego_vehicle.ego_id)
    
    #game = HybridGame(scenario_id)
    #game.generate_uppaal_model()

    scenario, planning_problem_set = CommonRoadFileReader(f"car/scenarios/{scenario_id}.xml").open()
    game_config = Configuration(scenario_id, "game")

    c_path = "car/shield/logic_scenario.c"
    o_path = "car/shield/logic_scenario.o"
    so_path = "car/shield/logic_scenario.so"

    c_builder = C_Builder(c_path, o_path, so_path, scenario, game_config)
    c_builder.write_c_file()
    c_builder.compile_c_file()