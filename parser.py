import os
import json
import pickle
from openai import OpenAI
from git import Repo
import boto3
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Function to read files from a directory
def read_files_from_directory(directory_path):
    code_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if is_non_code_file(file_path) or is_non_code_file_by_content(file_path):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code_files.append((file_path, f.read()))
            except UnicodeDecodeError:
                continue
    return code_files

# Function to read files from git repo
def read_files_from_git_repo(repo_url, local_path):
    Repo.clone_from(repo_url, local_path)
    return read_files_from_directory(local_path)

# Function to read files from S3
def read_files_from_s3(bucket_name, prefix):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    code_files = []
    for obj in response.get('Contents', []):
        file_key = obj['Key']
        file_content = s3.get_object(Bucket=bucket_name, Key=file_key)['Body'].read().decode('utf-8')
        code_files.append((file_key, file_content))
    return code_files

# Function to detect language
def detect_language(file_name, code):
    try:
        lexer = guess_lexer_for_filename(file_name, code)
        return lexer.name
    except ClassNotFound:
        return 'Unknown'

# Function to check if a file is non-code
NON_CODE_EXTENSIONS = {'.pyc', '.pyo', '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.log'}
NON_CODE_DIRECTORIES = {'venv', 'node_modules', '_pycache_', '.git', '.idea'}

def is_non_code_file(file_path):
    _, ext = os.path.splitext(file_path)
    if ext in NON_CODE_EXTENSIONS:
        return True
    for non_code_dir in NON_CODE_DIRECTORIES:
        if non_code_dir in file_path:
            return True
    return False

# Function to check if a file is non-code by content
def is_non_code_file_by_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('#!') or first_line.startswith('<?xml'):
                return True
    except UnicodeDecodeError:
        return True
    return False

# Function to organize files
def organize_files(code_files):
    organized_files = {}
    for file_path, content in code_files:
        language = detect_language(file_path, content)
        if language not in organized_files:
            organized_files[language] = []
        organized_files[language].append((file_path, content))
    return organized_files

# Step 1: Chunking the Code
def read_file_chunks(file_path, chunk_size=4000):
    with open(file_path, 'r', encoding='utf-8') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk

def collect_code_chunks(organized_files, chunk_size=4000):
    code_chunks = []
    for language, files in organized_files.items():
        for file_path, content in files:
            for chunk in read_file_chunks(file_path, chunk_size):
                code_chunks.append((file_path, language, chunk))
    return code_chunks

# Step 2: Contextual Summarization
def summarize_code_chunk(chunk, language, metadata, directory_structure):
    file_path, language, chunk_content = chunk
    metadata_info = metadata.get(file_path, {})
    directory_info = directory_structure.get(os.path.dirname(file_path), {})
    
    prompt = f"Summarize the following {language} code chunk:\n\n{chunk_content}\n\n"
    prompt += f"File Metadata: {json.dumps(metadata_info, indent=4)}\n"
    prompt += f"Directory Structure: {json.dumps(directory_info, indent=4)}\n"
    
    response = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": prompt,
        }],
        model="gpt-3.5-turbo",
    )
    return response['choices'][0]['message']['content']

# Step 3: Hierarchical Approach
def generate_high_level_summary(summaries):
    combined_summary = "\n\n".join(summaries)
    response = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": f"Generate a high-level summary for the following code summaries:\n\n{combined_summary}",
        }],
        model="gpt-3.5-turbo",
    )
    return response['choices'][0]['message']['content']

def generate_detailed_documentation(chunk, language, metadata, directory_structure):
    file_path, language, chunk_content = chunk
    metadata_info = metadata.get(file_path, {})
    directory_info = directory_structure.get(os.path.dirname(file_path), {})
    
    prompt = f"Generate detailed documentation for the following {language} code chunk:\n\n{chunk_content}\n\n"
    prompt += f"File Metadata: {json.dumps(metadata_info, indent=4)}\n"
    prompt += f"Directory Structure: {json.dumps(directory_info, indent=4)}\n"
    
    response = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": prompt,
        }],
        model="gpt-3.5-turbo",
    )
    return response['choices'][0]['message']['content']

def combine_documentation(high_level_summary, detailed_docs):
    detailed_docs_combined = "\n\n".join(detailed_docs)
    response = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": f"Combine the following high-level summary with the detailed documentation:\n\nHigh-level summary:\n{high_level_summary}\n\nDetailed documentation:\n{detailed_docs_combined}",
        }],
        model="gpt-3.5-turbo",
    )
    return response['choices'][0]['message']['content']

# Main function to parse project and collect information
def parse_project(directory):
    code_files = read_files_from_directory(directory)
    organized_files = organize_files(code_files)
    
    with open('organized_files.pkl', 'wb') as f:
        pickle.dump(organized_files, f)
    
    # Step 1: Chunking
    code_chunks = collect_code_chunks(organized_files)
    
    # Load metadata and directory structure JSON files
    with open('file_metadata.json', 'r') as f:
        metadata = json.load(f)
    with open('file_structure.json', 'r') as f:
        directory_structure = json.load(f)
    
    # Step 2: Summarize chunks
    # summaries = [summarize_code_chunk(chunk, chunk[1], metadata, directory_structure) for chunk in code_chunks]
    
    # # Step 3: Generate high-level summary
    # high_level_summary = generate_high_level_summary(summaries)
    
    # Generate detailed documentation
    detailed_docs = [generate_detailed_documentation(chunk, chunk[1], metadata, directory_structure) for chunk in code_chunks]
    
    # Combine documentation
    # final_documentation = combine_documentation(high_level_summary, detailed_docs)
    
    return detailed_docs


# Example usage
if __name__ == "__main__":
    directory_path = 'C:/Users/user/Temp-nik/cloned_repos/pathfinding-algorithm-visualizer'
    final_documentation = parse_project(directory_path)
    print(final_documentation)
