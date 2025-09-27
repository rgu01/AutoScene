import re
import subprocess
from collections import defaultdict
import car.utils.simulation as simulate

class Transition:
    def __init__(self, model_from, loc_from, model_to, loc_to, details, condition):
        self.model_from = model_from
        self.loc_from = loc_from
        self.model_to = model_to
        self.loc_to = loc_to
        self.details = details
        self.condition = condition

    def __repr__(self):
        return (f"Action(type={self.loc_from}, "
                f"value={self.details}")

class State:
    def __init__(self, state_info):
        self.state_info = state_info
        self.locations = self.parse_locations()
        self.variables = self.parse_variables()
        self.conditions = self.parse_conditions()
        self.transitions = self.parse_transitions()
        self.wait_transitions = self.parse_wait_transitions()
    
    def __eq__(self, other):
        return (self.locations == other.locations and
                self.variables == other.variables and 
                self.conditions == other.conditions and
                self.transitions == other.transitions and
                self.wait_transitions == self.wait_transitions)


    def __repr__(self):
        transitions_repr = ', '.join(repr(t) for t in self.transitions.values())
        return (f"State(locations={self.locations}, "
                f"variables={self.variables}, \n"
                f"transitions=[{transitions_repr}])")

    
    def __hash__(self):
        def make_hashable(obj):
            if isinstance(obj, dict):
                return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
            elif isinstance(obj, list):
                return tuple(make_hashable(i) for i in obj)
            elif isinstance(obj, set):
                return tuple(sorted(make_hashable(i) for i in obj))
            else:
                return obj

        return hash((
            make_hashable(self.locations),
            make_hashable(self.variables),
            make_hashable(self.conditions),
            make_hashable(self.transitions),
            make_hashable(self.wait_transitions)
        ))

    def parse_locations(self):
        locations = {}
        start_index = self.state_info.find("(")
        end_index = self.state_info.find(")")
        if start_index != -1 and end_index != -1:
            location_info = self.state_info[start_index+1:end_index].strip()
            location_pairs = location_info.split()
            for pair in location_pairs:
                model, location = pair.split(".")
                locations[model] = location
        return locations

    def parse_variables(self):
        variables = {}
        # Updated pattern to handle nested fields and arrays
        variable_pattern = re.compile(r"(\w+(?:\[\d+\])?(?:\.\w+(?:\[\d+\])?)*)=([\w\d-]+)")
        matches = variable_pattern.findall(self.state_info)
        for match in matches:
            full_var, value = match
            parts = full_var.split('.')
            current_level = variables
            for part in parts[:-1]:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            # Ensure the value is correctly parsed as an integer
            value = int(re.match(r'-?\d+', value).group())
            current_level[parts[-1]] = value
        return variables

    def parse_conditions(self):
        conditions = []
        condition_pattern = re.compile(r"When you are in \((.*?)\)")
        matches = condition_pattern.findall(self.state_info)
        for match in matches:
            if match.strip() not in conditions:
                conditions.append(match.strip())
        return conditions

    def parse_transitions(self):
        transitions_by_condition = defaultdict(list)
        transition_pattern = re.compile(r"When you are in \((.*?)\), take transition (\w+)\.(\w+)->(\w+)\.(\w+) \{(.*?)\}")
        matches = transition_pattern.findall(self.state_info)
        for match in matches:
            condition, model_from, loc_from, model_to, loc_to, details = match
            transition = Transition(model_from, loc_from, model_to, loc_to, details.strip(), condition.strip())
            transitions_by_condition[condition.strip()].append(transition)
        
        return transitions_by_condition

    def parse_wait_transitions(self):
        wait_transitions = []
        wait_pattern = re.compile(r"While you are in\s*\((.*?)\), wait")
        matches = wait_pattern.findall(self.state_info)
        for match in matches:
            wait_transitions.append(match.strip())
        return wait_transitions
    
class TiGaStrategy:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_text_file()
        self.states = self.parse_states()

    def load_text_file(self):
        with open(self.file_path, 'r') as file:
            data = file.read()
        return data

    def parse_states(self):
        states = []
        state_sections = self.data.split("State:")
        for section in state_sections[1:]:
            state_info = section.strip()
            states.append(State(state_info))
        return states

    def get_initial_state(self):
        start_index = self.data.find("Initial state:")
        end_index = self.data.find("Strategy to avoid losing:")
        if start_index != -1 and end_index != -1:
            return self.data[start_index:end_index].strip()
        return None

    def get_strategy(self):
        start_index = self.data.find("Strategy to avoid losing:")
        if start_index != -1:
            return self.data[start_index:].strip()
        return None
    
    def simulate(self, script_path:str, scenario_path:str, sampling_path:str):
        try:
            subprocess.run(["bash", script_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            simulate.generate(scenario_path, sampling_path, False)
        except subprocess.CalledProcessError as e:
            print("Error:\n", e.stderr)