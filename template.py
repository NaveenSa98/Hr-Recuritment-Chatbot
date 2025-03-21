import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

project_name = 'hr-chatbot'

list_of_files = [
    f"{project_name}/actions/__init__.py",
    f"{project_name}/actions/actions.py",
    f"{project_name}/actions/ats_integration.py",
    f"{project_name}/actions/calendar_integration.py",
    f"{project_name}/actions/logging.py",
    
    f"{project_name}/data/nlu.yml",
    f"{project_name}/data/stories.yml",
    f"{project_name}/data/rules.yml",
    f"{project_name}/data/domain.yml",
    
    f"{project_name}/models/.gitkeep",
    
    f"{project_name}/tests/test_nlu.py",
    f"{project_name}/tests/test_stories.py",
    f"{project_name}/tests/test_actions.py",
    
    f"{project_name}/logs/chatbot_logs.json",
    f"{project_name}/logs/chatbot_logs.csv",
    
    f"{project_name}/config.yml",
    f"{project_name}/credentials.yml",
    f"{project_name}/endpoints.yml",
    f"{project_name}/Dockerfile",
    f"{project_name}/requirements.txt",
    f"{project_name}/README.md",
    f"{project_name}/app.py",
  
]

for file in list_of_files:
    file = Path(file)
    filedir, filename = os.path.split(file)

    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for the file: {filename}")

    if not os.path.exists(file) or os.path.getsize(file) == 0:
        with open(file, 'w') as f:
            pass
        logging.info(f"Creating empty file: {file}")
    else:
        logging.info(f"File already exists: {file}")