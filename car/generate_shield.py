from utils.cps import Shield_V1 as Shield
import subprocess
import generate_cr_scenarios as gif
from crime import evaluate

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
        #evaluate.measure_single_criticality(f"{scenario_id}-shielded")
        #evaluate.measure_multiple_criticality(f"{scenario_id}-shielded")
    #only_compile()
    #if run_command(simulate_path):
    #    gif.generate()