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

        cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            department VARCHAR(50) NOT NULL,
            description TEXT ,
            requirements TEXT NOT NULL,
            salary_range VARCHAR(50),
            benefits TEXT,
            location VARCHAR(200),
            job_type VARCHAR(50),  
            status VARCHAR(50) DEFAULT 'OPEN',
                    
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")


        cur.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                candidate_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                resume_data BYTEA,
                resume_filename VARCHAR(255),
                    
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );""")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                application_id SERIAL PRIMARY KEY,
                candidate_id INTEGER REFERENCES candidates(candidate_id),
                job_id INTEGER REFERENCES jobs(job_id),
                status VARCHAR(50) NOT NULL DEFAULT 'not_started',

                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );""")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS interviews (
                interview_id SERIAL PRIMARY KEY,
                application_id INTEGER REFERENCES applications(application_id),
                interview_date DATE NOT NULL,
                interview_time TIME NOT NULL,
                interview_type VARCHAR(20) NOT NULL DEFAULT 'virtual',
                interviewer VARCHAR(100),
                notes TEXT,
                status VARCHAR(50) DEFAULT 'scheduled'
            );
            """)
        
        conn.commit()
        print ("Tables created successfully")
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

    



           
        