import os
import sys
import psycopg2
from dotenv import load_dotenv

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