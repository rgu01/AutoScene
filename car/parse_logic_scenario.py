import yaml
from utils.tiga_strategy import TiGaStrategy

class LogicScenarioConfig:
    def __init__(self, scenario_id: str):
        if not isinstance(scenario_id, str):
            raise TypeError("Expected scenario_id as a string")

        # Load YAML file
        path = f"car/scenarios/config_files/{scenario_id}-logic.yaml"
        with open(path, "r") as f:
            dictionary = yaml.safe_load(f)

        # Convert dict into dot-accessible attributes
        self._populate(dictionary)

    def _populate(self, dictionary: dict):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                nested = LogicScenarioConfig.__new__(LogicScenarioConfig)  # create empty instance
                nested._populate(value)  # fill recursively
                setattr(self, key, nested)
            else:
                setattr(self, key, value)

class LogicScenario(TiGaStrategy):
    def update_paras(self, config):
        config.ego_vehicle.ego_id = 3
        return config


if __name__ == '__main__':
    scenario_id = "DEU_A9-2_1_T-1"
    config = LogicScenarioConfig(scenario_id)
    logic_scenario_path = f"car/shield/{scenario_id}_{config.logic_params.type}.json"
    cutin = LogicScenario(logic_scenario_path)
    cutin.update_paras(config)
    print(config.ego_vehicle.ego_id)