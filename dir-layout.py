import os
import json

def get_file_structure(directory_path):
    file_structure = {}

    for root, dirs, files in os.walk(directory_path):
        # Get the relative path of the current directory
        relative_path = os.path.relpath(root, directory_path)
        # Initialize the current directory in the file structure
        current_dir = file_structure
        if relative_path != '.':
            for part in relative_path.split(os.sep):
                current_dir = current_dir.setdefault(part, {})
        # Add files to the current directory
        for file in files:
            current_dir[file] = None
        # Add subdirectories to the current directory
        for dir in dirs:
            current_dir[dir] = {}

    return file_structure

def save_file_structure(file_structure, file_path):
    with open(file_path, 'w') as f:
        json.dump(file_structure, f, indent=4)

def load_file_structure(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
    

if __name__ == "__main__":
    directory_path = ''
    file_structure = get_file_structure(directory_path)
    save_file_structure(file_structure, 'file_structure.json')

    # Load the file structure later
    loaded_file_structure = load_file_structure('file_structure.json')
    print(json.dumps(loaded_file_structure, indent=4))