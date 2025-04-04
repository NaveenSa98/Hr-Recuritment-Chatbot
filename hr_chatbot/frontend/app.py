from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import os
import sys
import json
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import queries as db_queries

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

RASA_API_URL = "http://localhost:5005/webhooks/rest/webhook"

app = Flask(__name__, 
            static_folder='static', 
            template_folder='templates')
CORS(app)

@app.route('/')
def index():
    """Render the main page with chatbot"""
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            logger.error("No data received in webhook")
            return jsonify({"error": "No data received"}), 400
            
        user_message = data.get('message', '')
        logger.info(f"Received message: {user_message}")

        # Forward to Rasa
        logger.info(f"Sending to Rasa: {user_message}")
        rasa_response = requests.post(
            RASA_API_URL,
            json={"sender": "user", "message": user_message}
        )
        rasa_response.raise_for_status()
        
        rasa_response_json = rasa_response.json()
        logger.info(f"Rasa response: {json.dumps(rasa_response_json)}")

        # Process all responses from Rasa
        responses = []
        for message in rasa_response_json:
            if 'text' in message:
                responses.append({
                    "type": "text",
                    "content": message['text']
                })
            if 'buttons' in message:
                responses.append({
                    "type": "buttons",
                    "content": message['buttons']
                })
            if 'custom' in message:
                # Extract the custom content without nesting
                custom_content = message['custom']
                # Remove double nesting if it exists
                if isinstance(custom_content, dict) and 'custom' in custom_content:
                    custom_content = custom_content['custom']
                
                logger.info(f"Processed custom payload: {json.dumps(custom_content)}")
                responses.append({
                    "type": "custom",
                    "content": custom_content
                })
        
        # If no responses were generated, add a fallback message
        if not responses:
            responses.append({
                "type": "text",
                "content": "I'm not sure how to respond to that. Can you try asking in a different way?"
            })
        
        logger.info(f"Sending responses to client: {json.dumps(responses)}")
        return jsonify({'responses': responses})

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return jsonify({
            'responses': [{
                'type': 'text',
                'content': "Sorry, I'm having trouble connecting to the chatbot service."
            }]
        }), 502
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'responses': [{
                'type': 'text',
                'content': "Sorry, an unexpected error occurred."
            }]
        }), 500

@app.route('/submit-application', methods=['POST'])
def submit_application():
    try:
        # Process form data with new fields
        first_name = request.form.get('firstName', '').strip()
        last_name = request.form.get('lastName', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        education = request.form.get('education', '').strip()
        position = request.form.get('position', '').strip()
        
        # Debug log received form data
        logger.info(f"Received form data: first_name={first_name}, last_name={last_name}, "
                    f"email={email}, phone={phone}, education={education}, position={position}")
        
        # Validate required fields
        required_fields = {
            'First Name': first_name,
            'Last Name': last_name,
            'Email': email,
            'Phone': phone,
            'Education': education,
            'Position': position
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            logger.warning(f"Missing required fields: {missing_fields_str}")
            return jsonify({
                "success": False,
                "message": f"Required fields missing: {missing_fields_str}"
            }), 400

        # Handle file upload
        resume = request.files.get('resume')
        if not resume or resume.filename == '':
            logger.warning("Resume file is missing")
            return jsonify({
                "success": False,
                "message": "Resume file is required"
            }), 400

        # Save resume and get path
        try:
            resume_path = db_queries.save_resume_file(resume)
            logger.info(f"Resume saved at: {resume_path}")
        except Exception as e:
            logger.error(f"Failed to save resume: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Failed to save resume: {str(e)}"
            }), 500
        
        # Store candidate information
        try:
            candidate_id = db_queries.insert_candidate_info(
                first_name, last_name, email, phone, position, education, resume_path
            )
            if not candidate_id:
                logger.error("Failed to store candidate information - no candidate ID returned")
                raise ValueError("No candidate ID returned")
            logger.info(f"Candidate stored with ID: {candidate_id}")
        except Exception as e:
            logger.error(f"Failed to store candidate information: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Failed to store candidate information: {str(e)}"
            }), 500
        
        # create application
        try:
            job_id = db_queries.get_job_id_by_title(position)
            if not job_id:
                logger.warning(f"Invalid job position: {position}")
                return jsonify({
                    "success": False,
                    "message": f"Invalid job position: {position}"
                }), 400
            
            # Create application with candidate_id and job_id
            application_id = db_queries.create_application(candidate_id, job_id)
            if not application_id:
                raise ValueError("Failed to create application")
            
            logger.info(f"Application created with ID: {application_id}")
            
            #  Return success with application_id
            return jsonify({
                "success": True,
                "message": "Application submitted successfully",
                "application_id": application_id
            })
            
        except Exception as e:
            logger.error(f"Failed to create application: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Failed to create application: {str(e)}"
            }), 500
        
    except Exception as e:
        logger.error(f"Error processing application: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to process application: {str(e)}"
        }), 500
    

@app.route('/confirm-interview', methods=['POST'])
def confirm_interview_endpoint():
    """
    Endpoint to confirm an interview directly from the frontend
    """
    try:
        data = request.json
        interview_id = data.get('interview_id')
        application_id = data.get('application_id')
        interview_date = data.get('date')
        interview_time = data.get('time')
        
        if not interview_id or not application_id:
            return jsonify({
                'success': False,
                'message': 'Missing required parameters'
            }), 400
        
        # Log the confirmation attempt
        print(f"Confirming interview via direct endpoint: interview_id={interview_id}, application_id={application_id}")
        
        # Check if the interview is still available
        interview_details = db_queries.get_interview_details(interview_id)
        if not interview_details:
            return jsonify({
                'success': False,
                'message': 'Interview not found'
            }), 404
            
        if interview_details.get('status') != 'available':
            return jsonify({
                'success': False,
                'message': 'This interview slot is no longer available. Please select another slot.'
            }), 400
        
        # Update the database
        success = db_queries.confirm_interview(interview_id, application_id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to confirm interview'
            }), 500
        
        # Get candidate email for the response
        application_info = db_queries.get_application_status(application_id)
        candidate_email = application_info.get("email", "") if application_info else ""
        
        # Create confirmation message
        confirmation_message = (
            f"Your interview has been successfully scheduled for {interview_date} at {interview_time}. "
            f"A confirmation email has been sent to {candidate_email}. "
            f"Please make sure to prepare for your interview and be on time. "
            f"If you need to reschedule, please contact our HR team at least 24 hours before your scheduled interview."
        )
        
        return jsonify({
            'success': True,
            'message': confirmation_message
        })
    
    except Exception as e:
        print(f"Error in confirm-interview endpoint: {e}")
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500


    
if __name__ == '__main__':
    app.run(debug=True, port=3000)