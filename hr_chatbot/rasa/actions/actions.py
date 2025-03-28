from typing import Any,Text,Dict,List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..'))
sys.path.insert(0, project_root)

from database.queries import (
    get_all_jobs_openings, 
    get_jobs_by_department, 
    get_jobs_by_title, 
    get_job_requirements
)




class ActionListJobs(Action):
    """ 
    fetch all jobs from database

    """
    def name(self) -> Text:
        return "action_list_jobs"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            # Check if department is specified
            department = tracker.get_slot("department")

            if department:
                try:
                    job_listings = get_jobs_by_department(department)
                    if job_listings:
                        dispatcher.utter_message(
                            f"Here are the current openings in the {department} department:\n\n{job_listings}"
                        )
                    else:
                        dispatcher.utter_message(
                            f"I couldn't find any open positions in the {department} department at the moment."
                        )
                except Exception as e:
                    dispatcher.utter_message("Sorry, I encountered an issue fetching job listings for this department.")
                    print(f"Error fetching jobs by department: {e}")  # Log the error for debugging
            else:
                try:
                    job_listings = get_all_jobs_openings()
                    if job_listings:
                        dispatcher.utter_message(
                            "Here are our current job openings:\n\n" + job_listings
                        )
                    else:
                        dispatcher.utter_message(
                            "I couldn't find any open positions at the moment. Please check back later or visit our careers page."
                        )
                except Exception as e:
                    dispatcher.utter_message("Sorry, I encountered an issue fetching job listings.")
                    print(f"Error fetching all job openings: {e}")  # Log the error for debugging

        except Exception as e:
            dispatcher.utter_message("An unexpected error occurred. Please try again later.")
            print(f"Unexpected error in ActionListJobs: {e}")  # Log the error for debugging

        return []