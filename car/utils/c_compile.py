import subprocess

def compile_c_file(c_path:str, o_path:str, so_path:str):
    try:
        # Run the first command to compile the shield.c file
        subprocess.run(['gcc', '-c', '-fPIC', c_path, '-o', o_path], check=True)
        
        # Run the second command to create the shared library
        subprocess.run(['gcc', '-shared', '-o', so_path, o_path], check=True)
        
        print(f"Shared library created successfully at {so_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}")
    except FileNotFoundError:
        print("GCC is not installed or not found in your PATH.")