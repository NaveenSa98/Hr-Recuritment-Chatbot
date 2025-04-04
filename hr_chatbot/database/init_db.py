import os 
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

def connect_to_db():
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
    
def create_table():
    conn = connect_to_db()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()

        # Enable UUID extension for other tables
        cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            title VARCHAR(200) NOT NULL,
            department VARCHAR(50) NOT NULL,
            description TEXT,
            requirements TEXT NOT NULL,
            salary_range VARCHAR(50),
            benefits TEXT,
            location VARCHAR(200),
            job_type VARCHAR(50),  
            status VARCHAR(50) DEFAULT 'OPEN',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            first_name VARCHAR(25) NOT NULL,
            last_name  VARCHAR(25) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            position VARCHAR(20) NOT NULL,
            education VARCHAR(200),
            resume_path VARCHAR(255),
            status VARCHAR(50) NOT NULL DEFAULT 'received',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            application_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY (START WITH 10000 INCREMENT BY 1),

            candidate_id UUID NOT NULL,
            job_id UUID NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'under_review',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            interview_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            application_id INTEGER NOT NULL,
            interview_date DATE NOT NULL,
            interview_time TIME NOT NULL,
            interview_type VARCHAR(20) NOT NULL DEFAULT 'virtual',
            interviewer VARCHAR(100),
            notes TEXT,
            status VARCHAR(50) NOT NULL DEFAULT 'available'
        );
        """)

        # Creating indexes for faster queries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
            CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);
            CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status);
            CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
            CREATE INDEX IF NOT EXISTS idx_applications_candidate ON applications(candidate_id);
            CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id);
            CREATE INDEX IF NOT EXISTS idx_interviews_application ON interviews(application_id);
            CREATE INDEX IF NOT EXISTS idx_interviews_date ON interviews(interview_date);
            CREATE INDEX IF NOT EXISTS idx_interviews_status ON interviews(status);
        """)

        conn.commit()
        print("Tables created successfully")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error creating tables: {e}")
        return False
    finally:
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")

if __name__ == "__main__":
    create_table()
