import re
from collections import defaultdict
import subprocess
import generate_cr_scenarios as gif
from crime import evaluate

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
        if not isinstance(other, CPS_State):
            return False
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

class CPS_State:
    def __init__(self, position, velocity, acceleration, orientation):
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.orientation = orientation

    def __eq__(self, other):
        if not isinstance(other, CPS_State):
            return False
        return (self.position == other.position and
                self.velocity == other.velocity and
                self.acceleration == other.acceleration and
                self.orientation == other.orientation)

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
            make_hashable(self.position),
            make_hashable(self.velocity),
            make_hashable(self.acceleration),
            make_hashable(self.orientation)
        ))


    def __repr__(self):
        return (f"CPS_State(position={self.position}, velocity={self.velocity}, "
                f"acceleration={self.acceleration}, orientation={self.orientation})")


class Shield:
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

    def get_c_header(self):
        strategy_entries = []
        
        for state_obj in self.states:
            count = state_obj.variables.get("count",{})
            phase = state_obj.variables.get("phase",{})
            # Extract cps_state
            cps_state = state_obj.variables.get("cps_state", {})
            cps_position = cps_state.get("position", {"x": 0, "y": 0})
            cps_velocity = cps_state.get("vel", 0)
            cps_orientation = cps_state.get("head", 0)
            cps_acceleration = cps_state.get("acc", 0)

            # Extract all obs_states
            obs_states = []
            for i in range(100):  # Assuming a maximum of 100 obstacles
                obs_key = f"obs_state[{i}]"
                if obs_key in state_obj.variables:
                    obs_state = state_obj.variables[obs_key]
                    obs_position = obs_state.get("position", {"x": 0, "y": 0})
                    obs_velocity = obs_state.get("vel", 0)
                    obs_orientation = obs_state.get("head", 0)
                    obs_acceleration = obs_state.get("acc", 0)
                    obs_states.append(f"""
                                        {{{{{obs_position["x"]}, {obs_position["y"]} }}, {obs_velocity}, {obs_orientation}, {obs_acceleration}}}
                    """)

            # Determine action and character based on transitions
            for condition, transitions in state_obj.transitions.items():
                #if transitions is not None and "Move" in transitions[0].loc_from and len(transitions) < 3 and cps_velocity > 900 and cps_velocity < 4800:
                #    list_exception_states.append(state_obj)
                for transition in transitions:
                    character = None
                    action = None
                    if "Move" in transition.loc_from:
                        character = 'M'
                        action = int(transition.details.split('go(')[1].split(')')[0])  # Extract action number
                    elif "Turn" in transition.loc_from:
                        character = 'T'
                        action = int(transition.details.split('turn(')[1].split(')')[0])  # Extract action number
                    
                    if action is not None:
                        # Add to strategy entries
                        obs_array = "                   ,".join(obs_states)
                        if obs_states:
                            strategy_entries.append(f"""
                                {{
                                    {{
                                        {{{{{cps_position["x"]}, {cps_position["y"]}}}, {cps_velocity}, {cps_orientation}, {cps_acceleration}}}, {phase}, {count},
                                        {{
                                            {obs_array}
                                        }}
                                    }},
                                    {{'{character}', {action}}}
                                }}
                            """)
                        else:
                            strategy_entries.append(f"""
                                {{
                                    {{
                                        {{{{{cps_position["x"]}, {cps_position["y"]}}}, {cps_velocity}, {cps_orientation}, {cps_acceleration}}}, {phase}, {count}
                                    }},
                                    {{'{character}', {action}}}
                                }}
                            """)

        strategy_array = f"const int SLEN = {len(strategy_entries)};\nconst ST_ENTRY strategy[{len(strategy_entries)}] = {{{', '.join(strategy_entries)}}};"
        return strategy_array

    def insert_strategy_into_c_file(self, c_file_path):
        strategy_array = self.get_c_header()
        
        # Determine the number of obstacles
        max_obs = 0
        for state_obj in self.states:
            for i in range(100):  # Assuming a maximum of 100 obstacles
                if f"obs_state[{i}]" in state_obj.variables:
                    max_obs = max(max_obs, i + 1)

        # Read the existing content of the C file
        with open(c_file_path, 'r') as file:
            c_file_content = file.read()

        # Update the value of MAXOBS
        maxobs_pattern = re.compile(r"#define MAXOBS\s+\d+")
        c_file_content = maxobs_pattern.sub(f"#define MAXOBS {max_obs}", c_file_content)

        # Replace the content between "// strategy starts" and "// strategy ends" with strategy_array
        strategy_pattern = re.compile(r"// strategy starts.*?// strategy ends", re.DOTALL)
        c_file_content = strategy_pattern.sub(f"// strategy starts\n{strategy_array}\n// strategy ends", c_file_content)

        # Write the updated content back to the C file
        with open(c_file_path, 'w') as file:
            file.write(c_file_content)
    
    def compile_c_file(self):
        try:
            # Run the first command to compile the shield.c file
            subprocess.run(['gcc', '-c', '-fPIC', 'car/shield/shield.c', '-o', 'car/shield/shield.o'], check=True)
            
            # Run the second command to create the shared library
            subprocess.run(['gcc', '-shared', '-o', 'car/shield/libshield.so', 'car/shield/shield.o'], check=True)
            
            print("Shared library libshield.so created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while executing the command: {e}")
        except FileNotFoundError:
            print("GCC is not installed or not found in your PATH.")

def run_command(script_path):
    try:
        result = subprocess.run(["bash", script_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        #print("Output:\n", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Error:\n", e.stderr)
        return False


def only_compile():
    # Create an instance of the Shield class and parse the text file
    shield_instance = Shield('car/shield/safeCarObs.json')
    # Print the C header code
    shield_instance.insert_strategy_into_c_file("car/shield/shield.c")
    # Compile the c code
    shield_instance.compile_c_file()

if __name__ == '__main__':
    # Specify the file path to process
    scenario_id = "DEU_A9-2_1_T-1"
    scenario_path = f"car/scenarios/{scenario_id}.xml"
    simulate_path = "car/shield/linux_simulate.sh"
    synthsis_path = "car/shield/linux_synthesis.sh"
    # execute(verifyta_path, uppaal_file_path, synthesis_query_path)
    #evaluate.measure_criticality(scenario_id)
    if run_command(synthsis_path):
        gif.generate(scenario_path, True)
        evaluate.measure_single_criticality(f"{scenario_id}-shielded")
        evaluate.measure_multiple_criticality(f"{scenario_id}-shielded")
    #only_compile()
    #if run_command(simulate_path):
    #    gif.generate()