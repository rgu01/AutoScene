import re
import subprocess
from utils.tiga_strategy import State

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

class Shield_V1:
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
