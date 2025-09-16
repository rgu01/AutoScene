import yaml

class Configuration:
    def __init__(self, scenario_id: str, suffix):
        if not isinstance(scenario_id, str):
            raise TypeError("Expected scenario_id as a string")

        # Load YAML file
        path = f"car/config/{scenario_id}-{suffix}.yaml"
        with open(path, "r") as f:
            dictionary = yaml.safe_load(f)

        # Convert dict into dot-accessible attributes
        self._populate(dictionary)

    def _populate(self, dictionary: dict):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                nested = Configuration.__new__(Configuration)  # create empty instance
                nested._populate(value)  # fill recursively
                setattr(self, key, nested)
            else:
                setattr(self, key, value)