import os 
import pymysql
from pymysql import Error
from dotenv import load_dotenv

load_dotenv()

def connect_to_db():
    try:
        conn = pymysql.connect(
            db=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"Error connecting to MySQL database: {e}")
        return None
    
def create_table():
    conn = connect_to_db()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()



        cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id VARCHAR(36) PRIMARY KEY ,
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
            candidate_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
            first_name VARCHAR(25) NOT NULL,
            last_name VARCHAR(25) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            position VARCHAR(50) NOT NULL,
            education VARCHAR(200),
            resume_path VARCHAR(255),
            status VARCHAR(50) NOT NULL DEFAULT 'received',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            application_id INT AUTO_INCREMENT PRIMARY KEY,
            candidate_id CHAR(36) NOT NULL,
            job_id CHAR(36) NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'under_review',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
        );
        """)

        # Alter the auto_increment start value
        cur.execute("ALTER TABLE applications AUTO_INCREMENT = 10000;")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            interview_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
            application_id INT NOT NULL,
            interview_date DATE NOT NULL,
            interview_time TIME NOT NULL,
            interview_type VARCHAR(20) NOT NULL DEFAULT 'virtual',
            interviewer VARCHAR(100),
            notes TEXT,
            status VARCHAR(50) NOT NULL DEFAULT 'available',
            FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE
        );
        """)

        # Creating indexes for faster queries
        cur.execute("CREATE INDEX idx_jobs_status ON jobs(status);")
        cur.execute("CREATE INDEX idx_candidates_email ON candidates(email);")
        cur.execute("CREATE INDEX idx_candidates_status ON candidates(status);")
        cur.execute("CREATE INDEX idx_applications_status ON applications(status);")
        cur.execute("CREATE INDEX idx_applications_candidate ON applications(candidate_id);")
        cur.execute("CREATE INDEX idx_applications_job ON applications(job_id);")
        cur.execute("CREATE INDEX idx_interviews_application ON interviews(application_id);")
        cur.execute("CREATE INDEX idx_interviews_date ON interviews(interview_date);")
        cur.execute("CREATE INDEX idx_interviews_status ON interviews(status);")

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
            print("MySQL connection is closed")

if __name__ == "__main__":
    create_table()