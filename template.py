import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s')

project_name = 'hr_chatbot'

list_of_files = [
    f"{project_name}/rasa/actions/__init__.py",
    f"{project_name}/rasa/actions/actions.py",
   
    f"{project_name}/rasa/data/nlu.yml",
    f"{project_name}/rasa/data/rules.yml",
    f"{project_name}/rasa/data/stories.yml",
 
    f"{project_name}/rasa/models/.gitkeep", 

    f"{project_name}/rasa/config.yml",
    f"{project_name}/rasa/credentials.yml",
    f"{project_name}/rasa/domain.yml",
    f"{project_name}/rasa/endpoints.yml",

    f"{project_name}/tests/test_actions.py",
    f"{project_name}/database/init_db.py",
    f"{project_name}/database/queries.py",
    f"{project_name}/database/sample_data.sql",
    

    f"{project_name}/Dockerfile",
    f"{project_name}/docker-compose.yml",

    f"{project_name}/README.md",
    f"{project_name}/requirements.txt",
    f"{project_name}/.env",
]

for file in list_of_files:
    file = Path(file)
    filedir, filename = os.path.split(file)

    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for the file: {filename}")

    if not os.path.exists(file) or os.path.getsize(file) == 0:
        with open(file, 'w') as f:
            pass  # Creating an empty file
        logging.info(f"Creating empty file: {file}")
    else:
        logging.info(f"File already exists: {file}")
