import re
import subprocess
import numpy as np
from utils.config import Configuration as GameConfiguration
from commonroad.scenario.scenario import Scenario

class C_Builder:
    def __init__(self, c_path:str, o_path:str, so_path:str, scenario: Scenario, config:GameConfiguration):
          self.c_path = c_path
          self.o_path = o_path
          self.so_path = so_path
          self.scenario = scenario
          self.config = config

    def write_c_file(self):
        # Read the existing content of the C file
        with open(self.c_path, 'r') as file:
            c_file_content = file.read()

        # Update the parameters
        para_pattern = re.compile(r"#define MAXP\s+\d+")
        c_file_content = para_pattern.sub(f"#define MAXP {self.config.MAXP}", c_file_content)
        para_pattern = re.compile(r"#define MAXPRE\s+\d+")
        c_file_content = para_pattern.sub(f"#define MAXPRE {self.config.MAXPRE}", c_file_content)
        para_pattern = re.compile(r"#define MAXSUC\s+\d+")
        c_file_content = para_pattern.sub(f"#define MAXSUC {self.config.MAXSUC}", c_file_content)

        lanelet_pattern = re.compile(
            r"/\*\*capture lanelet start \*/.*?/\*\*capture lanelet end \*/",
            re.DOTALL
        )
        c_file_content = lanelet_pattern.sub(
            f"/**capture lanelet start */\n{self.translate_lanelet_to_cstr()}\n/**capture lanelet end */",
            c_file_content
        )


        # Write the updated content back to the C file
        with open(self.c_path, 'w') as file:
            file.write(c_file_content)

    def compile_c_file(self):
        try:
            # Run the first command to compile the shield.c file
            subprocess.run(['gcc', '-c', '-fPIC', self.c_path, '-o', self.o_path], check=True)
            
            # Run the second command to create the shared library
            subprocess.run(['gcc', '-shared', '-o', self.so_path, self.o_path], check=True)
            
            print(f"Shared library created successfully at {self.so_path}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while executing the command: {e}")
        except FileNotFoundError:
            print("GCC is not installed or not found in your PATH.")

    def calculate_travel_time(self, lanelet):
            left_bound_points = lanelet.left_vertices
            right_bound_points = lanelet.right_vertices

            # Calculate the length of the left bound
            left_length = np.sum(np.sqrt(np.sum(np.diff(left_bound_points, axis=0)**2, axis=1)))

            # Calculate the length of the right bound
            right_length = np.sum(np.sqrt(np.sum(np.diff(right_bound_points, axis=0)**2, axis=1)))

            # Average the lengths of the left and right bounds to get the lanelet length
            lanelet_length = (left_length + right_length) / 2

            return lanelet_length

    def translate_lanelet_to_cstr(self, points_per_line=4):
        """
        Generate C code for ST_LANE laneNet[MAXL] with multi-line ST_DPOINT arrays.
        
        points_per_line: number of ST_DPOINTs per line in C for readability.
        """
        laneNet_entries = []

        for lane in self.scenario.lanelet_network.lanelets:
            # compute lane length as double
            travel_time = self.calculate_travel_time(lane)
            lane_length = float(travel_time)

            # lane info
            lane_ID = lane.lanelet_id
            lane_predecessor = lane.predecessor if lane.predecessor else []
            lane_successor = lane.successor if lane.successor else []
            lane_adjLeft = lane.adj_left
            lane_adjRight = lane.adj_right

            # lane markings
            lane_markingLeft = lane.line_marking_left_vertices.value == 'dashed'
            lane_markingRight = lane.line_marking_right_vertices.value == 'dashed'

            # direction flags
            lane_dirLeft = bool(lane.adj_left_same_direction)
            lane_dirRight = bool(lane.adj_right_same_direction)

            # vertices as double
            leftLane = lane._left_vertices.astype(float)
            rightLane = lane._right_vertices.astype(float)

            # merge points if straight line
            if np.all(leftLane[:, 1] == leftLane[0, 1]) or np.all(leftLane[:, 0] == leftLane[0, 0]):
                leftLane = leftLane[[0, -1]]
            if np.all(rightLane[:, 1] == rightLane[0, 1]) or np.all(rightLane[:, 0] == rightLane[0, 0]):
                rightLane = rightLane[[0, -1]]

            # padding
            pad_len_left = self.config.MAXP - len(leftLane)
            if pad_len_left > 0:
                padding_left = np.full((pad_len_left, 2), np.nan)
            else:
                padding_left = np.empty((0, 2))
            leftLane_full = np.vstack([leftLane, padding_left])

            pad_len_right = self.config.MAXP - len(rightLane)
            if pad_len_right > 0:
                padding_right = np.full((pad_len_right, 2), np.nan)
            else:
                padding_right = np.empty((0, 2))
            rightLane_full = np.vstack([rightLane, padding_right])

            # helper to format points with line breaks
            def format_points(points_array):
                lines = []
                for i in range(0, len(points_array), points_per_line):
                    chunk = points_array[i:i + points_per_line]
                    line = ", ".join(
                        f"{{{pt[0]:.6f}, {pt[1]:.6f}}}" if not np.isnan(pt[0]) else "{NONE, NONE}"
                        for pt in chunk
                    )
                    lines.append(line)
                return ",\n        ".join(lines)

            leftLane_str = "{\n        " + format_points(leftLane_full) + "\n    }"
            leftLane_inline = f"{{{leftLane_str}, {'true' if lane_markingLeft else 'false'}}}"

            rightLane_str = "{\n        " + format_points(rightLane_full) + "\n    }"
            rightLane_inline = f"{{{rightLane_str}, {'true' if lane_markingRight else 'false'}}}"

            # pad predecessors/successors
            lane_predecessor += [None] * (self.config.MAXPRE - len(lane_predecessor))
            lane_successor += [None] * (self.config.MAXSUC - len(lane_successor))
            pre_str = ", ".join("None" if x is None else str(x) for x in lane_predecessor)
            suc_str = ", ".join("None" if x is None else str(x) for x in lane_successor)

            # full ST_LANE entry
            lane_entry = (
                f"{{{lane_ID}, {leftLane_inline}, {rightLane_inline}, "
                f"{pre_str}, {suc_str}, "
                f"{'None' if lane_adjLeft is None else lane_adjLeft}, "
                f"{'true' if lane_dirLeft else 'false'}, "
                f"{'None' if lane_adjRight is None else lane_adjRight}, "
                f"{'true' if lane_dirRight else 'false'}, "
                f"{lane_length:.6f}}}"
            )

            laneNet_entries.append(lane_entry)

        # final C array
        laneNet_str = "ST_LANE laneNet[MAXL] = {\n" + ",\n".join(laneNet_entries) + "\n};"
        return laneNet_str
