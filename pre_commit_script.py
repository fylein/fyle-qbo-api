import os
import subprocess

# Specify the root directory of your repository
repo_path = './'


def auto_format_repo():
    # Walk through all files in the repository
    for root, dirs, files in os.walk(repo_path):
        for file_name in files:
            if file_name.endswith('.py'):  # Process only Python files
                file_path = os.path.join(root, file_name)
                format_file(file_path)


def format_file(file_path):
    try:
        subprocess.run(['autopep8', '--in-place', '--aggressive', file_path], check=True)
        print(f'Formatted: {file_path}')
    except subprocess.CalledProcessError:
        print(f'Error formatting: {file_path}')


if __name__ == '__main__':
    auto_format_repo()
