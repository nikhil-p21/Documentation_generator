import os
from git import Repo
import boto3
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound
import pickle

# read files from a directory 
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

#read files 
def read_files_from_git_repo(repo_url, local_path):
    Repo.clone_from(repo_url, local_path)
    return read_files_from_directory(local_path)

def read_files_from_s3(bucket_name, prefix):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    code_files = []
    for obj in response.get('Contents', []):
        file_key = obj['Key']
        file_content = s3.get_object(Bucket=bucket_name, Key=file_key)['Body'].read().decode('utf-8')
        code_files.append((file_key, file_content))
    return code_files

def detect_language(file_name, code):
    try:
        lexer = guess_lexer_for_filename(file_name, code)
        return lexer.name
    except ClassNotFound:
        return 'Unknown'

#identifying non-code or data files (env files)
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

def is_non_code_file_by_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('#!') or first_line.startswith('<?xml'):
                return True
    except UnicodeDecodeError:
        return True
    return False

def organize_files(code_files):
    organized_files = {}
    for file_path, content in code_files:
        language = detect_language(file_path, content)
        if language not in organized_files:
            organized_files[language] = []
        organized_files[language].append((file_path, content))
    return organized_files

# Example usage
if __name__ == "__main__":
    directory_path = ''
    code_files = read_files_from_directory(directory_path)
    organized_files = organize_files(code_files)
    with open('organized_files.pkl','wb') as f:
        pickle.dump(organized_files,f)
    for language, files in organized_files.items():
        print(f'Language: {language}, Number of Files: {len(files)}')