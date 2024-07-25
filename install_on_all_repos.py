import os
import subprocess

def main(inp_parent_dir):
    subdirs = [d for d in os.listdir(inp_parent_dir) if os.path.isdir(os.path.join(inp_parent_dir, d))]

    for subdir in subdirs:
        subdir_path = os.path.join(inp_parent_dir, subdir)
        print(f"Reinitializing .git in {subdir_path}")
        subprocess.run(['git', 'init'], cwd=subdir_path)


if __name__ == "__main__":
    exitLoop = False
    print("This program will run 'git init' on all directories within the parent directory inputted.")
    while not exitLoop:
        parent_dir = input("Enter the path to the parent directory or type 'exit' to exit: ")
        if os.path.isdir(parent_dir):
            main(parent_dir)
        elif parent_dir == "exit":
            print("Exiting process...")
            exitLoop = True
        else:
            print("Please enter a valid path.")