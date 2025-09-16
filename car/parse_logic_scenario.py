from utils.tiga_strategy import TiGaStrategy
from utils.config import Configuration as LogicScenarioConfig
from utils.hybrid_game import HybridGame

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