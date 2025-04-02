import os
import sys
import psycopg2
import random
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from datetime import datetime

# Determine the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

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

def get_all_jobs_openings(active_only=True):
    """Fetch all jobs, optionally filtering for active jobs only"""
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
    
        formatted_output = "\n".join(f"- {title}" for title in titles)
        
        return formatted_output 
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

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
        
        # Let the database generate the application_id automatically
        cur.execute("""
            INSERT INTO applications (candidate_id, job_id, status, applied_at, last_updated)
            VALUES (%s, %s, 'form_completed', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING application_id
        """, (candidate_id, job_id))
        
        result = cur.fetchone()
        conn.commit()
        
        if result:
            return result[0]  # Return the application_id
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
            SELECT status, application_id
            FROM applications
            WHERE application_id = %s
        """, (application_id,))
        
        result = cur.fetchone()
        return result if result else None
    except Exception as e:
        print(f"Error getting application details: {e}")
        return None
    finally:
        if conn:
            cur.close()
            conn.close()


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