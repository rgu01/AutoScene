from car.utils.tiga_strategy import TiGaStrategy
from car.utils.config import Configuration as LogicScenarioConfig
from car.utils.hybrid_game import HybridGame
from car.utils.c_compile import C_Builder

class LogicScenario(TiGaStrategy):
    def update_paras(self, config):
        config.ego_vehicle.ego_id = 3
        return config

if __name__ == '__main__':
    scenario_id = "DEU_A9-2_1_T-1"

    config = LogicScenarioConfig(scenario_id, "logic")
    logic_scenario_path = f"car/shield/{scenario_id}_{config.logic_params.type}.json"
    cutin = LogicScenario(logic_scenario_path)
    cutin.update_paras(config)
    print(config.ego_vehicle.ego_id)
    
    game = HybridGame(scenario_id)
    game.generate_uppaal_model()

    c_path = "car/shield/logic_scenario.c"
    o_path = "car/shield/logic_scenario.o"
    so_path = "car/shield/logic_scenario.so"

    c_builder = C_Builder(c_path, o_path, so_path, game.scenario, game.config)
    c_builder.write_c_file()
    c_builder.compile_c_file()