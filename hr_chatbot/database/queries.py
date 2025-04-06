import os
import sys
import psycopg2
import random
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta, date


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


load_dotenv()

# database connection
def connect_to_db():
    """
    Establish a connection to the PostgreSQL database.
    
    Returns:
    - psycopg2 connection object or None if connection fails
    """
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Fetch all job openings as a list (new function)
def get_all_jobs_as_list(active_only=True):
    """Fetch all jobs as a list, optionally filtering for active jobs only"""
    conn = connect_to_db() 
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        query = "SELECT title FROM jobs"
        if active_only:
            query += " WHERE status = 'OPEN'"
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query)
        titles = [row[0] for row in cursor.fetchall()] 
        
        return titles
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

# Fetch jobs by department
def get_jobs_by_department(department, active_only=True):
    """Fetch jobs filtered by department and return formatted details for chatbot"""
    conn = connect_to_db()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        query = """
            SELECT title, department, description, requirements, salary_range, 
                   benefits, location, job_type 
            FROM jobs WHERE LOWER(department) = LOWER(%s)
        """
        if active_only:
            query += " AND status = 'OPEN'"
        query += " ORDER BY job_id DESC"
        
        cursor.execute(query, (department,))
        jobs = cursor.fetchall()
        
        job_details = []
        for job in jobs:
            formatted_job = f"""
Title: {job[0]}
Department: {job[1]}
Description: {job[2]}
Requirements: {job[3]}
Salary Range: {job[4]}
Benefits: {job[5]}
Location: {job[6]}
Job Type: {job[7]}
"""
            job_details.append(formatted_job.strip())
        
        return "\n\n".join(job_details)
    
    except Exception as e:
        print(f"Error fetching jobs by department: {e}")
        return ""
    finally:
        if conn:
            cursor.close()
            conn.close()


# Fetch job details by title
def get_job_requirements(title):
    """Fetch key job details needed for chatbot"""
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        query = """
            SELECT title, requirements,location,description, salary_range,benefits  
            FROM jobs 
            WHERE title ILIKE %s 
            AND status = 'OPEN'
            ORDER BY created_at DESC 
            LIMIT 1
        """
        
        cursor.execute(query, (f"%{title}%",))
        job = cursor.fetchone()
        
        if not job:
            return None
            
        # Return as dictionary with specific fields
        return {
            'title': job[0],
            'requirements': job[1],
            'location': job[2],
            'description': job[3],
            'salary_range': job[4],
            'benefits': job[5]
        }
        
    except Exception as e:
        print(f"Error fetching job details: {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()


# Save resume 
def save_resume_file(resume_file):
    """
    Save the uploaded resume file to a specified directory.
    """
    if not resume_file:
        return None
    
    try:
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        filename = secure_filename(resume_file.filename)
        # Fix: Use datetime.now() instead of datetime.datetime.now()
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"

        file_path = os.path.join(upload_dir, unique_filename)
        resume_file.save(file_path)

        return os.path.join('uploads', unique_filename)
    except Exception as e:
        print(f"Error saving resume file: {e}")
        return None

# Insert candidate information into the database
def insert_candidate_info(first_name, last_name, email, phone, position, education, resume_path):
    """
    Insert candidate information into the database.
    """
    conn = connect_to_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        # Fix: SQL parameters should match the values (7 parameters, not 8)
        cursor.execute("""INSERT INTO candidates (first_name, last_name, email, phone, position, education, resume_path) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s)
                          RETURNING candidate_id
                       """, (first_name, last_name, email, phone, position, education, resume_path))
        
        candidate_id = cursor.fetchone()[0]
        conn.commit()
        return candidate_id
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error inserting candidate info: {e}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()


# Create a new application record linking a candidate to a job            
def create_application(candidate_id, job_id):
    """
    Create a new application record linking a candidate to a job
    Returns application_id if successful, None otherwise
    """
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        
      
        cur.execute("""
            INSERT INTO applications (candidate_id, job_id, status, applied_at, last_updated)
            VALUES (%s, %s, ' under_review', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING application_id
        """, (candidate_id, job_id))
        
        result = cur.fetchone()
        conn.commit()
        
        if result:
            return result[0] 
        return None
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error creating application: {e}")
        return None
    finally:
        if conn:
            cur.close()
            conn.close()


# Fetch job ID by title
def get_job_id_by_title(title):
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT job_id FROM jobs
            WHERE title = %s AND status = 'OPEN'
            LIMIT 1
        """, (title,))
        
        result = cur.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error getting job ID: {e}")
        return None
    finally:
        if conn:
            cur.close()
            conn.close()

#  Fetch application details by application ID
def get_application_by_id(application_id):
    """
    Fetch application details by application ID.
    """
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT a.application_id, a.status, j.title, c.first_name, c.last_name, c.email
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN candidates c ON a.candidate_id = c.candidate_id
            WHERE a.application_id = %s
        """, (application_id,))
        
        result = cur.fetchone()
        if result:
            return {
                "application_id": result[0],
                "status": result[1],
                "job_title": result[2],
                "candidate_name": f"{result[3]} {result[4]}",
                "email": result[5]
            }
        return None
    except Exception as e:
        print(f"Error getting application details: {e}")
        return None
    finally:
        if conn:
            cur.close()
            conn.close()

# Update application status
def get_application_status(application_id):
    """
    Get the status of an application
    """
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT a.status, j.title, c.first_name, c.last_name, c.email
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN candidates c ON a.candidate_id = c.candidate_id
            WHERE a.application_id = %s
        """, (application_id,))
        
        result = cur.fetchone()
        if result:
            return {
                "status": result[0],
                "job_title": result[1],
                "candidate_name": f"{result[2]} {result[3]}",
                "email": result[4]
            }
        return None
    except Exception as e:
        print(f"Error fetching application status: {e}")
        return None
    finally:
        if conn:
            cur.close()
            conn.close()

# Get available interview slots for an application
def get_available_interview_slots(application_id):
    """
    Get available interview slots for an application
    """
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        

        cur.execute("""
            SELECT job_id FROM applications WHERE application_id = %s
        """, (application_id,))
        
        app_result = cur.fetchone()
        if not app_result:
            return None
        
        job_id = app_result['job_id']
        
        cur.execute("""
            SELECT interview_id, interview_date, interview_time, interview_type, interviewer
            FROM interviews
            WHERE status = 'available' AND application_id = %s
            ORDER BY interview_date, interview_time
        """, (application_id,))
        
        slots = cur.fetchall()

        for slot in slots:

            if isinstance(slot['interview_date'], datetime) or isinstance(slot['interview_date'], date):
                slot['interview_date'] = slot['interview_date'].strftime('%Y-%m-%d')
                

            if hasattr(slot['interview_time'], 'strftime'): 
                slot['interview_time'] = slot['interview_time'].strftime('%H:%M:%S')
                

            if hasattr(slot['interview_id'], 'hex'):  
                slot['interview_id'] = str(slot['interview_id'])
                
        return slots
    except Exception as e:
        print(f"Error fetching interview slots: {e}")
        return None
    finally:
        if conn:
            cur.close()
            conn.close()


# Get interview details by interview ID
def get_interview_details(interview_id):
    """
    Get details for a specific interview slot
    """
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT interview_id, interview_date, interview_time, interview_type, interviewer, status, notes
            FROM interviews
            WHERE interview_id = %s
        """, (interview_id,))
        
        result = cur.fetchone()
        
    
        if result:
        
            if 'interview_date' in result:
                if isinstance(result['interview_date'], datetime) or isinstance(result['interview_date'], date):
                    result['interview_date'] = result['interview_date'].strftime('%Y-%m-%d')
            
          
            if 'interview_time' in result and hasattr(result['interview_time'], 'strftime'):
                result['interview_time'] = result['interview_time'].strftime('%H:%M:%S')
                

            if 'interview_id' in result and hasattr(result['interview_id'], 'hex'):
                result['interview_id'] = str(result['interview_id'])
                
        return result
    except Exception as e:
        print(f"Error fetching interview details: {e}")
        return None
    finally:
        if conn:
            cur.close()
            conn.close()



# Confirm an interview by updating its status
def confirm_interview(interview_id, application_id):
    """
    Confirm an interview by updating its status to 'scheduled'
    """
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        cur = conn.cursor()
        
        print(f"Confirming interview: interview_id={interview_id}, application_id={application_id}")
        
      
        cur.execute("""
            SELECT status FROM interviews WHERE interview_id = %s
        """, (interview_id,))
        
        interview = cur.fetchone()
        if not interview:
            print(f"Interview not found: interview_id={interview_id}")
            return False
            
        print(f"Current interview status: {interview[0]}")
        

        cur.execute("""
            UPDATE interviews
            SET status = 'scheduled'
            WHERE interview_id = %s AND status = 'available'
        """, (interview_id,))
        
        rows_updated = cur.rowcount
        print(f"Interviews table rows updated: {rows_updated}")
        
        if rows_updated == 0:
            print("No rows updated in interviews table. Interview may already be scheduled.")
            
  
        cur.execute("""
            UPDATE applications
            SET status = 'interview_scheduled'
            WHERE application_id = %s
        """, (application_id,))
        
        app_rows_updated = cur.rowcount
        print(f"Applications table rows updated: {app_rows_updated}")
        
        conn.commit()
        

        return rows_updated > 0 or app_rows_updated > 0
    except Exception as e:
        conn.rollback()
        print(f"Error confirming interview: {e}")
        return False
    finally:
        if conn:
            cur.close()
            conn.close()

# Get scheduled interview for an application
def get_scheduled_interview(application_id):
    """
    Get the scheduled interview for an application
    """
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT interview_id, interview_date, interview_time, interview_type, interviewer, status, notes
            FROM interviews
            WHERE application_id = %s AND status = 'scheduled'
            ORDER BY interview_date, interview_time
            LIMIT 1
        """, (application_id,))
        
        result = cur.fetchone()
        
        if result:
           
            if 'interview_date' in result:
                if isinstance(result['interview_date'], datetime) or isinstance(result['interview_date'], date):
                    result['interview_date'] = result['interview_date'].strftime('%Y-%m-%d')
            
           
            if 'interview_time' in result and hasattr(result['interview_time'], 'strftime'):
                result['interview_time'] = result['interview_time'].strftime('%H:%M:%S')
                
          
            if 'interview_id' in result and hasattr(result['interview_id'], 'hex'):
                result['interview_id'] = str(result['interview_id'])
                
        return result
    except Exception as e:
        print(f"Error fetching scheduled interview: {e}")
        return None
    finally:
        if conn:
            cur.close()
            conn.close()