import os
import sys
from rasa_sdk.events import SlotSet

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# Import directly from the database module
from database.queries import (
    get_all_jobs_openings, 
    get_jobs_by_department, 
    get_job_requirements
)

class ActionFetchJobs(Action):
    def name(self) -> Text:
        """Unique identifier for the action."""
        return "action_fetch_jobs"

    def run(self, 
            dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Fetch job openings based on user's request.
        
        If a department is specified in the tracker, fetch jobs for that department.
        Otherwise, fetch all open job titles.
        """
        # Check if a department was mentioned in the user's message
        department = next(tracker.get_latest_entity_values("department"), None)
        
        try:
            if department:
                # Fetch jobs for a specific department
                jobs = get_jobs_by_department(department)
                
                if jobs:
                    dispatcher.utter_message(f"Here are the job openings in the {department} department:\n{jobs}")
                else:
                    dispatcher.utter_message(f"Sorry, no open positions found in the {department} department.")
            else:
                # Fetch all job openings
                jobs = get_all_jobs_openings()
                
                if jobs:
                    response = "Current Job Openings:\n" + jobs
                    dispatcher.utter_message(response)
                else:
                    dispatcher.utter_message("Sorry, no job openings are currently available.")
        
        except Exception as e:
            dispatcher.utter_message(f"An error occurred while fetching job openings: {str(e)}")
        
        return []


# Add any additional custom actions here
class ActionCheckJobRequirements(Action):
    def name(self) -> Text:
        return "action_check_requirements"
    
    def run(self, 
            dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Try to get job title from entities first
        job_title = next(tracker.get_latest_entity_values("job_title"), None)
        
        # If no entity found, try to extract from the latest user message
        if not job_title:
            latest_message = tracker.latest_message.get('text', '')
            if "qualifications for" in latest_message.lower():
                job_title = latest_message.split("qualifications for")[-1].strip()
            elif "requirements for" in latest_message.lower():
                job_title = latest_message.split("requirements for")[-1].strip()
            else:
                job_title = ' '.join(latest_message.split()[-2:]).strip('?')
        
        if not job_title:
            dispatcher.utter_message("Please specify a job title to check requirements.")
            return []
        
        try:
            from database.queries import get_job_requirements
            
            job_title = job_title.lower().strip()
            job_details = get_job_requirements(job_title)
            
            if job_details:
                response_lines = [
                    f"✨ **Job Requirements & Details: {job_details['title']}** ✨\n"
                ]
                
                # Location
                if job_details.get('location'):
                    response_lines.append(f"📍 **Location:** {job_details['location']}  \n")
                
                # Requirements
                if job_details.get('requirements'):
                    requirements = "\n  - " + "\n  - ".join(job_details['requirements'].split("\n"))
                    response_lines.append(f"📌 **Requirements:**{requirements}  \n")
                
                # Description
                if job_details.get('description'):
                    response_lines.append(f"📝 **Job Description:**  \n{job_details['description']}  \n")
                
                # Salary Range
                if job_details.get('salary_range'):
                    response_lines.append(f"💰 **Salary Range:** {job_details['salary_range']}  \n")
                
                # Benefits
                if job_details.get('benefits'):
                    benefits = "\n✅ " + "\n✅ ".join(job_details['benefits'].split("\n"))
                    response_lines.append(f"🎁 **Benefits:**  \n{benefits}  \n")
                
                response_lines.append("👉 **For more details, check our job portal.**  \n")
                
                response = "\n".join(response_lines)
                dispatcher.utter_message(response)
            else:
                dispatcher.utter_message(f"No details found for: {job_title}. Please check the job title.")
        
        except Exception as e:
            dispatcher.utter_message("Sorry, I couldn't retrieve the job details at the moment.")
        
        return []