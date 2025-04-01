import os
import sys
from rasa_sdk.events import SlotSet
import random
import string


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from database import queries as db_queries

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from database.queries import (
    get_all_jobs_openings, 
    get_jobs_by_department, 
    get_job_requirements,
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
                
                response_lines.append("👉 **To apply to the position \n Say 'start application' to begin.**  \n")
                
                response = "\n".join(response_lines)
                dispatcher.utter_message(response)
            else:
                dispatcher.utter_message(f"No details found for: {job_title}. Please check the job title.")
        
        except Exception as e:
            dispatcher.utter_message("Sorry, I couldn't retrieve the job details at the moment.")
        
        return []
    

class ActionShowApplicationForm(Action):
    def name(self) -> Text:
        return "action_show_application_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        job_title = tracker.get_slot("job_title") or "the position"
        
        form_data = {
            "payload": "application_form",
            "title": "Please complete the application form below:",
            "elements": [
                {
                    "type": "text",
                    "name": "firstName",
                    "label": "First Name *",
                    "required": True
                },
                {
                    "type": "text",
                    "name": "lastName",
                    "label": "Last Name *",
                    "required": True
                },
                {
                    "type": "tel",
                    "name": "phone",
                    "pattern": "[0-9]{10,15}",
                    "label": "Phone Number *",
                    "required": True
                },
                {
                    "type": "email",
                    "name": "email",
                    "label": "Email Address *",
                    "required": True
                },
                {
                    "type": "text",
                    "name": "education",
                    "label": "Education *",
                    "required": True
                },
                {
                    "type": "text",
                    "name": "position",
                    "label": "Position Applying For ",
                    "value": job_title,
                    "required": True
                },
                {
                    "type": "file",
                    "name": "resume",
                    "label": "Upload your CV Here *",
                    "accept": ".pdf",
                    "required": True,
                    "help": "drop files here"
                },
                {
                    "type": "action",
                    "element": {
                        "type": "button",
                        "name": "submit",
                        "label": "Submit Application",
                        "action": "submit_application_form"
                    }
                }
            ]
        }

        dispatcher.utter_message(json_message={"custom": form_data})
        return []
    
class ActionProcessApplication(Action):
    def name(self) -> Text:
        return "action_process_application"
    
    def run(self, 
            dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text = "I've recevied your application form! Processing your information....")

        return [SlotSet("application_stage", "form_completed")]
    

class ActionStoreApplication(Action):
    def name(self) -> Text:
        return "action_store_application"
    
    def run(self, 
            dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        application_id = str(random.randint(10000, 99999))

        return [SlotSet("application_id", application_id)]
    
class ActionCheckStatus(Action):
    def name(self) -> Text:
        return "action_check_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        application_id = tracker.get_slot("application_id")
        
        if not application_id:
            dispatcher.utter_message(text="I need your application ID to check your status.")
            return []
        
        # Remove any non-numeric characters if present
        if not application_id.isdigit():
            # Extract numeric part
            app_id = ''.join(filter(str.isdigit, application_id))
            if not app_id:
                dispatcher.utter_message(text="Please provide a valid application ID which should be a numeric value.")
                return []
            application_id = app_id
        
        # Get application status from database
        application_info = db_queries.get_application_status(application_id)
        
        if not application_info:
            dispatcher.utter_message(text=f"I couldn't find any application with ID {application_id}. Please check if the ID is correct.")
            return []
        
        # Update slots
        job_title = application_info["job_title"]
        status = application_info["status"]
        
        return [
            SlotSet("job_title", job_title),
            SlotSet("application_stage", status)
        ]

        


    
    


