import os
import sys
from rasa_sdk.events import SlotSet
from database import queries as db_queries
from typing import Any, Text, Dict, List
from datetime import datetime
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from database.queries import (
    get_all_jobs_as_list, 
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
       
        department = next(tracker.get_latest_entity_values("department"), None)
        
        try:
            if department:
                # Fetch jobs for specific department
                jobs = get_jobs_by_department(department)
                
                if jobs:
                    dispatcher.utter_message(f"Here are the job openings in the {department} department:\n{jobs}")
                else:
                    dispatcher.utter_message(f"Sorry, no open positions found in the {department} department.")
            else:
                # Fetch all jobs
                job_list = get_all_jobs_as_list()
                
                if job_list:
                    # First, send an intro message
                    dispatcher.utter_message("Current Job Openings:")
                    
                    # Then send buttons for each job
                    buttons = []
                    for job_title in job_list:
                        # Create a button for each job with payload to trigger job requirements
                        buttons.append({
                            "title": job_title,
                            "payload": f"/ask_job_requirements{{\"job_title\":\"{job_title}\"}}"
                        })
                    
                    # Send buttons as a separate message
                    dispatcher.utter_message(buttons=buttons)
                else:
                    dispatcher.utter_message("Sorry, no job openings are currently available.")
        
        except Exception as e:
            dispatcher.utter_message(f"An error occurred while fetching job openings: {str(e)}")
        
        return []

# Fetching job requirements
class ActionCheckJobRequirements(Action):
    def name(self) -> Text:
        return "action_check_requirements"
    
    def run(self, 
            dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
       
        job_title = next(tracker.get_latest_entity_values("job_title"), None)
        
       
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


# Action to show the application form
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
    
# Action to handle the application submission

class ActionProcessApplication(Action):
    def name(self) -> Text:
        return "action_process_application"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get application_id from slot
        application_id = tracker.get_slot("application_id")
        
        if not application_id:
            logger.warning("No application_id found in slots")
            dispatcher.utter_message(text="I couldn't find your application details. Please try submitting your application again.")
            return []
        
        logger.info(f"Processing application with ID: {application_id}")
        
        # Get application details from database
        application = db_queries.get_application_by_id(application_id)
        
        if not application:
            logger.warning(f"Application with ID {application_id} not found in database")
            dispatcher.utter_message(text="I couldn't find your application in our system. Please try submitting your application again.")
            return []
        
        # Send confirmation message with application ID
        confirmation_message = (
            f"Thank you for submitting your application! Your application ID is {application_id}. "
            f"Please save this ID for future reference. You can use it to check your application status later."
        )
        
        dispatcher.utter_message(text=confirmation_message)
        
        return [SlotSet("application_id", application_id)]


# Action to check the status of an application
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
        
      
        if not application_id.isdigit():
            
            app_id = ''.join(filter(str.isdigit, application_id))
            if not app_id:
                dispatcher.utter_message(text="Please provide a valid application ID which should be a numeric value.")
                return []
            application_id = app_id
        
       
        application_info = db_queries.get_application_status(application_id)
        
        if not application_info:
            dispatcher.utter_message(text=f"I couldn't find any application with ID {application_id}. Please check if the ID is correct.")
            return []
        
        # Update slots
        job_title = application_info["job_title"]
        status = application_info["status"]

        if status.lower() == "shortlisted":
            dispatcher.utter_message(text=f"Congratulations! Your application for {job_title} has been shortlisted. To continue the process, please schedule your interview at your earliest convenience.")
        else:
            # Handle other statuses
            dispatcher.utter_message(text=f"Your application for {job_title} is currently at stage: '{status}'.")
        
        return [
            SlotSet("job_title", job_title),
            SlotSet("application_stage", status)
        ]
    
# Action to schedule an interview
class ActionScheduleInterview(Action):
    def name(self) -> Text:
        return "action_schedule_interview"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        application_id = tracker.get_slot("application_id")
        
        if not application_id:
            dispatcher.utter_message(text="I need your application ID to check if you're eligible for an interview.")
            return []
        
   
        if not application_id.isdigit():
           
            app_id = ''.join(filter(str.isdigit, application_id))
            if not app_id:
                dispatcher.utter_message(text="Please provide a valid application ID which should be a numeric value.")
                return []
            application_id = app_id
       
        application_info = db_queries.get_application_status(application_id)
        
        if not application_info:
            dispatcher.utter_message(text=f"I couldn't find any application with ID {application_id}. Please check if the ID is correct.")
            return []
        
       
        status = application_info["status"]
        job_title = application_info["job_title"]
        
       
        if status.lower() == "interview_scheduled":
           
            scheduled_interview = db_queries.get_scheduled_interview(application_id)
            
            if scheduled_interview:
               
                interview_date = scheduled_interview.get("interview_date", "")
                interview_time = scheduled_interview.get("interview_time", "")
                interview_type = scheduled_interview.get("interview_type", "Virtual")
                interviewer = scheduled_interview.get("interviewer", "HR Team")
                
               
                if isinstance(interview_date, str) and not interview_date.startswith("20"):
                 
                    formatted_date = interview_date
                else:
                  
                    try:
                        if isinstance(interview_date, str):
                            date_obj = datetime.strptime(interview_date, "%Y-%m-%d")
                        else:
                            date_obj = interview_date
                        formatted_date = date_obj.strftime("%A, %B %d, %Y")
                    except:
                        formatted_date = str(interview_date)
                
                
                if isinstance(interview_time, str) and ":" in interview_time:
                    try:
                        time_obj = datetime.strptime(interview_time, "%H:%M:%S")
                        formatted_time = time_obj.strftime("%I:%M %p")
                    except:
                        formatted_time = interview_time
                else:
                    formatted_time = str(interview_time)
                
                
                message = (
                    f"You already have a scheduled interview for your application for {job_title}. "
                    f"Your interview is scheduled for {formatted_date} at {formatted_time}. "
                    f"It will be a {interview_type.lower()} interview with {interviewer}. "
                    f"If you need to reschedule, please contact our HR team directly."
                )
                
                dispatcher.utter_message(text=message)
                
                return [
                    SlotSet("job_title", job_title),
                    SlotSet("application_stage", status),
                    SlotSet("interview_date", formatted_date),
                    SlotSet("interview_time", formatted_time)
                ]
            else:
                
                dispatcher.utter_message(
                    text=f"Your application for {job_title} shows that you have a scheduled interview, but I couldn't find the details. Please contact our HR team for more information."
                )
                return [
                    SlotSet("job_title", job_title),
                    SlotSet("application_stage", status)
                ]
        
        
        if status.lower() != "shortlisted":
            dispatcher.utter_message(text=f"Your application for {job_title} is currently in '{status}' status. Only shortlisted candidates can schedule interviews.")
            return [
                SlotSet("job_title", job_title),
                SlotSet("application_stage", status)
            ]
        
        
        available_slots = db_queries.get_available_interview_slots(application_id)
        
        if not available_slots or len(available_slots) == 0:
            dispatcher.utter_message(text=f"There are no available interview slots for your application at the moment. Our HR team will contact you soon.")
            return [
                SlotSet("job_title", job_title),
                SlotSet("application_stage", status)
            ]
        
       
        buttons = []
        for slot in available_slots:
         
            if hasattr(slot["interview_date"], 'strftime'):
                date_str = slot["interview_date"].strftime("%A, %B %d, %Y")
            else:
                date_str = str(slot["interview_date"])
                
            if hasattr(slot["interview_time"], 'strftime'):
                time_str = slot["interview_time"].strftime("%I:%M %p")
            else:
                time_str = str(slot["interview_time"])
                
            interview_id = str(slot["interview_id"]) 
            
            payload = f'/select_interview_slot{{"interview_id":"{interview_id}","date":"{date_str}","time":"{time_str}","application_id":"{application_id}"}}'
            buttons.append({
                "title": f"{date_str} at {time_str}",
                "payload": payload
            })
        
        dispatcher.utter_message(
            text=f"Great! Your application for {job_title} has been shortlisted. Here are the available interview slots:",
            buttons=buttons
        )
        
        return [
            SlotSet("job_title", job_title),
            SlotSet("application_stage", status)
        ]


# Action to select an interview slot
class ActionSelectInterviewSlot(Action):
    def name(self) -> Text:
        return "action_select_interview_slot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        interview_id = tracker.get_slot("interview_id")
        interview_date = tracker.get_slot("interview_date")
        interview_time = tracker.get_slot("interview_time")
        application_id = tracker.get_slot("application_id")
        
        if not interview_id or not interview_date or not interview_time or not application_id:
            dispatcher.utter_message(text="I couldn't process your selection. Please try again.")
            return []
        
       
        interview_details = db_queries.get_interview_details(interview_id)
        
        if not interview_details:
            dispatcher.utter_message(text="Sorry, this interview slot is no longer available. Please select another slot.")
            return []
        
        
        if interview_details.get("status") != "available":
            dispatcher.utter_message(text="Sorry, this interview slot has already been taken. Please select another slot.")
            return []
        
     
        interview_type = interview_details.get("interview_type", "Virtual")
        interviewer = interview_details.get("interviewer", "HR Team")
        
       
        interview_payload = {
            "payload": "interview_details",
            "interview_id": str(interview_id),  
            "date": interview_date, 
            "time": interview_time,  
            "type": interview_type,
            "interviewer": interviewer,
            "application_id": str(application_id),  
            "job_title": tracker.get_slot("job_title") or "Applied Position"
        }

        
        dispatcher.utter_message(text=f"You've selected an interview slot for {interview_date} at {interview_time}. Here are the details:")
        dispatcher.utter_message(json_message={"interview_details": interview_payload})

         
        buttons = [
           
            {
                "title": "Select a different slot",
                "payload": f'/ask_interview_scheduling{{"application_id":"{application_id}"}}'
            }
        ]
        
        dispatcher.utter_message(
            buttons=buttons
        )
        
        
        
        dispatcher.utter_message(text="Please review the interview details above. If you'd like to accept this slot, click the 'Accept Interview' button. Otherwise, you can select a different slot.")
        
        return [
            SlotSet("interview_id", interview_id),
            SlotSet("interview_date", interview_date),
            SlotSet("interview_time", interview_time)
        ]


# Action to confirm the interview
class ActionConfirmInterview(Action):
    def name(self) -> Text:
        return "action_confirm_interview"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
       
        logger.info("ActionConfirmInterview started")
        
        
        interview_id = tracker.get_slot("interview_id")
        application_id = tracker.get_slot("application_id")
        interview_date = tracker.get_slot("interview_date")
        interview_time = tracker.get_slot("interview_time")

        logger.info(f"Slots: interview_id={interview_id}, application_id={application_id}, date={interview_date}, time={interview_time}")
        
        if not interview_id or not application_id:
            logger.warning("Missing required slots: interview_id or application_id")
            dispatcher.utter_message(text="I couldn't process your confirmation. Please try again.")
            return []
        
    
        logger.info(f"Confirming interview: interview_id={interview_id}, application_id={application_id}")
        success = db_queries.confirm_interview(interview_id, application_id)
        
        if not success:
            logger.error(f"Failed to confirm interview: interview_id={interview_id}, application_id={application_id}")
            dispatcher.utter_message(text="Sorry, there was an error confirming your interview. Please try again or contact HR directly.")
            return []

        application_info = db_queries.get_application_status(application_id)
        candidate_email = application_info.get("email", "") if application_info else ""

        logger.info(f"Interview confirmed successfully for {candidate_email}")

        confirmation_message = (
            f"Your interview has been successfully scheduled for {interview_date} at {interview_time}. "
            f"A confirmation email has been sent to {candidate_email}. "
            f"Please make sure to prepare for your interview and be on time. "
            f"If you need to reschedule, please contact our HR team at least 24 hours before your scheduled interview."
        )
        
        dispatcher.utter_message(text=confirmation_message)
        
        return [
            SlotSet("application_stage", "interview_scheduled")
        ]
