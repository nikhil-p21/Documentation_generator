import os
import json

def extract_file_metadata(directory_path):
    metadata = {}
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)
                metadata[file_path] = {
                    'size': file_size,
                    'last_modified': file_mtime
                }
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    with open('file_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)

# Example usage
if __name__ == "__main__":
    directory_path = 'C:/Users/user/Temp-nik/cloned_repos/pathfinding-algorithm-visualizer'
    extract_file_metadata(directory_path)
