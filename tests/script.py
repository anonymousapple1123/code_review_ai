# Create the project structure and files
import os

# Create directory structure
directories = [
    'code_review_app',
    'code_review_app/gui',
    'code_review_app/llm_interface', 
    'code_review_app/core_cpp',
    'code_review_app/utils',
    'code_review_app/config',
    'code_review_app/sandbox',
    'code_review_app/test_files'
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    
print("Project directory structure created successfully!")