import os
import psycopg2
from psycopg2 import sql
from datetime import datetime
import random
import string
from init_db import connect_to_db



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
            FROM jobs WHERE department = %s
        """
        if active_only:
            query += " AND status = 'OPEN'"
        query += " ORDER BY job_id DESC"
        
        cursor.execute(query, (department,))
        jobs = cursor.fetchall()
        
      
        job_details = []
        for job in jobs:
            formatted_job = f"""
Title: {job[1]}
Department: {job[2]}
Description: {job[3]}
Requirements: {job[4]}
Salary Range: {job[5]}
Benefits: {job[6]}
Location: {job[7]}
Job Type: {job[8]}
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


def get_job_by_title(title, active_only=True):
    """Fetch job by title"""
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        query = """SELECT title, department, description, requirements, salary_range, 
                          benefits, location, job_type 
                FROM jobs WHERE title ILIKE %s"""
        if active_only:
            query += " AND status = 'OPEN'" 
        query += " ORDER BY created_at DESC LIMIT 1"
        
        cursor.execute(query, (f"%{title}%",))
        job = cursor.fetchone()
        
        if not job:
            return None
            
       
        job_details = []
        for job in job:
            formatted_job = f"""
Title: {job[1]}
Department: {job[2]}
Description: {job[3]}
Requirements: {job[4]}
Salary Range: {job[5]}
Benefits: {job[6]}
Location: {job[7]}
Job Type: {job[8]}
"""
            job_details.append(formatted_job.strip())
        
        return "\n\n".join(job_details)
    except Exception as e:
        print(f"Error fetching job by title: {e}")
        return None
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
            SELECT title, requirements, department, location 
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
            'department': job[2],
            'location': job[3]
        }
        
    except Exception as e:
        print(f"Error fetching job details: {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()


def get_job_benefits(title):
    """Fetch ONLY job benefits by job title (case-insensitive search)"""
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT benefits 
                FROM jobs 
                WHERE title ILIKE %s 
                AND status = 'OPEN'
                ORDER BY created_at DESC 
                LIMIT 1
            """
            cursor.execute(query, (f"%{title}%",))
            result = cursor.fetchone()
            
            return result[0] if result else None
            
    except Exception as e:
        print(f"Error fetching job benefits: {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()


def create_or_update_candidate(name, email, phone=None, resume_data=None, resume_filename=None):
    """Create a new candidate or update if email exists"""
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Check if candidate exists
        cursor.execute("SELECT candidate_id FROM candidates WHERE email = %s", (email,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing candidate
            if resume_data:
                cursor.execute(
                    """
                    UPDATE candidates 
                    SET name = %s, phone = %s, resume_data = %s, resume_filename = %s, resume_uploaded_at = CURRENT_TIMESTAMP 
                    WHERE email = %s RETURNING candidate_id
                    """,
                    (name, phone, psycopg2.Binary(resume_data), resume_filename, email)
                )
            else:
                cursor.execute(
                    "UPDATE candidates SET name = %s, phone = %s WHERE email = %s RETURNING candidate_id",
                    (name, phone, email)
                )
            candidate_id = cursor.fetchone()[0]
        else:
            # Create new candidate
            if resume_data:
                cursor.execute(
                    """
                    INSERT INTO candidates 
                    (name, email, phone, resume_data, resume_filename, resume_uploaded_at) 
                    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP) 
                    RETURNING candidate_id
                    """,
                    (name, email, phone, psycopg2.Binary(resume_data), resume_filename)
                )
            else:
                cursor.execute(
                    "INSERT INTO candidates (name, email, phone) VALUES (%s, %s, %s) RETURNING candidate_id",
                    (name, email, phone)
                )
            candidate_id = cursor.fetchone()[0]
        
        conn.commit()
        return candidate_id
    except Exception as e:
        conn.rollback()
        print(f"Error creating/updating candidate: {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()



    