INSERT INTO jobs (title, department, description, requirements, location, salary_range, job_type)
VALUES 
('Software Engineer', 'engineering', 
'Join our engineering team to build innovative solutions for our clients. You will be responsible for designing, developing, and maintaining software applications.',
'- Bachelor''s degree in Computer Science or related field
- 3+ years of experience in software development
- Proficiency in Python, JavaScript, and SQL
- Experience with web frameworks like React, Angular, or Vue
- Strong problem-solving skills and attention to detail',
'Remote', '$80,000 - $120,000', 'Full-time'),

('Marketing Specialist', 'marketing',
'Drive our marketing initiatives and help grow our brand presence. You will be responsible for creating and implementing marketing strategies across various channels.',
'- Bachelor''s degree in Marketing or related field
- 2+ years of experience in digital marketing
- Experience with social media marketing and content creation
- Knowledge of SEO/SEM and analytics tools
- Excellent communication and creative skills',
'New York, NY', '$60,000 - $85,000', 'Full-time'),

('HR Coordinator', 'hr',
'Support our HR team in managing employee relations, recruitment, and administrative tasks. You will be the first point of contact for employee inquiries.',
'- Bachelor''s degree in Human Resources or related field
- 1+ years of experience in HR
- Knowledge of HR policies and procedures
- Excellent organizational and interpersonal skills
- Experience with HRIS systems is a plus',
'Chicago, IL', '$45,000 - $65,000', 'Full-time'),

('Data Analyst', 'engineering',
'Analyze complex data sets to provide insights that drive business decisions. You will work with cross-functional teams to identify trends and opportunities.',
'- Bachelor''s degree in Statistics, Mathematics, or related field
- 2+ years of experience in data analysis
- Proficiency in SQL, Python, and data visualization tools
- Experience with business intelligence platforms
- Strong analytical and problem-solving skills',
'Remote', '$70,000 - $95,000', 'Full-time'),

('Operations Manager', 'operations',
'Oversee daily operations and ensure efficiency across the organization. You will be responsible for process improvement and team management.',
'- Bachelor''s degree in Business Administration or related field
- 5+ years of experience in operations management
- Strong leadership and decision-making skills
- Experience with project management methodologies
- Excellent communication and interpersonal skills',
'Austin, TX', '$90,000 - $130,000', 'Full-time'),

('UX/UI Designer', 'engineering',
'Create intuitive and engaging user experiences for our digital products. You will collaborate with product and engineering teams to design user-centered solutions.',
'- Bachelor''s degree in Design, HCI, or related field
- 3+ years of experience in UX/UI design
- Proficiency in design tools like Figma, Sketch, or Adobe XD
- Portfolio demonstrating user-centered design process
- Experience with user research and usability testing',
'San Francisco, CA', '$85,000 - $115,000', 'Full-time'),

('Content Writer', 'marketing',
'Develop compelling content for our website, blog, and marketing materials. You will be responsible for creating content that engages our target audience.',
'- Bachelor''s degree in English, Journalism, or related field
- 2+ years of experience in content creation
- Excellent writing and editing skills
- Knowledge of SEO best practices
- Experience with content management systems',
'Remote', '$50,000 - $75,000', 'Full-time'),

('Financial Analyst', 'operations',
'Analyze financial data and prepare reports to guide business decisions. You will be responsible for budgeting, forecasting, and financial modeling.',
'- Bachelor''s degree in Finance, Accounting, or related field
- 3+ years of experience in financial analysis
- Proficiency in Excel and financial modeling
- Knowledge of accounting principles and financial statements
- Strong analytical and problem-solving skills',
'New York, NY', '$75,000 - $100,000', 'Full-time'),

('Customer Success Manager', 'operations',
'Ensure customer satisfaction and drive retention by building strong relationships with clients. You will be responsible for onboarding, training, and support.',
'- Bachelor''s degree in Business, Communications, or related field
- 3+ years of experience in customer success or account management
- Strong communication and relationship-building skills
- Experience with CRM systems
- Problem-solving and conflict resolution abilities',
'Remote', '$65,000 - $90,000', 'Full-time'),

('DevOps Engineer', 'engineering',
'Manage our infrastructure and deployment processes to ensure reliability and scalability. You will be responsible for automation, monitoring, and security.',
'- Bachelor''s degree in Computer Science or related field
- 4+ years of experience in DevOps or SRE
- Experience with cloud platforms (AWS, Azure, or GCP)
- Knowledge of containerization and orchestration tools
- Proficiency in scripting languages and CI/CD pipelines',
'Remote', '$90,000 - $130,000', 'Full-time');



INSERT INTO interviews (application_id, interview_date, interview_time, interview_type, interviewer, notes, status)
VALUES
    (10000, '2025-04-05', '10:00:00', 'virtual', 'John Doe', 'Initial HR screening.', 'available'),
    (10000, '2025-04-10', '14:30:00', 'onsite', 'Jane Smith', 'Technical round.', 'available'),
    (10000, '2025-04-15', '09:00:00', 'virtual', 'Mike Johnson', 'Final interview with CTO.', 'available'),

    (100001, '2025-04-07', '11:00:00', 'virtual', 'Alice Brown', 'HR discussion.', 'available'),
    (100001, '2025-04-12', '16:00:00', 'onsite', 'Robert Green', 'Technical panel discussion.', 'available'),
    (100001, '2025-04-18', '10:30:00', 'virtual', 'Emma Wilson', 'Final round.', 'available'),

    (10002, '2025-04-06', '09:45:00', 'virtual', 'Daniel Martinez', 'Phone screening.', 'available'),
    (10002, '2025-04-11', '13:15:00', 'onsite', 'Sophia Anderson', 'Coding challenge.', 'available'),
    (10002, '2025-04-17', '15:00:00', 'virtual', 'Christopher Harris', 'Final discussion.', 'available'),

    (10003, '2025-04-05', '14:00:00', 'virtual', 'Olivia Thompson', 'HR screening.', 'available'),
    (10003, '2025-04-09', '10:45:00', 'onsite', 'William Carter', 'Technical assessment.', 'available'),
    (10003, '2025-04-14', '11:30:00', 'virtual', 'Isabella Lewis', 'Final interview.', 'available'),

    (10004, '2025-04-08', '08:30:00', 'virtual', 'James Walker', 'Initial discussion.', 'available'),
    (10004, '2025-04-13', '17:00:00', 'onsite', 'Lucas Hall', 'Skill test.', 'available'),
    (10004, '2025-04-19', '12:00:00', 'virtual', 'Mia Allen', 'Offer discussion.', 'available'),

    (10005, '2025-04-07', '10:30:00', 'virtual', 'Charlotte Young', 'Recruiter screening.', 'available'),
    (10005, '2025-04-11', '14:45:00', 'onsite', 'Benjamin Scott', 'Tech interview.', 'available'),
    (10005, '2025-04-16', '09:15:00', 'virtual', 'Henry Nelson', 'Final discussion.', 'available'),

    (10006, '2025-04-06', '13:00:00', 'virtual', 'Amelia Roberts', 'HR interview.', 'available'),
    (10006, '2025-04-10', '15:30:00', 'onsite', 'Ethan Phillips', 'Live coding round.', 'available'),
    (10006, '2025-04-15', '10:00:00', 'virtual', 'Mason Evans', 'Final interview.', 'available'),

    (10007, '2025-04-09', '08:00:00', 'virtual', 'Harper Wright', 'HR screening.', 'available'),
    (10007, '2025-04-14', '12:45:00', 'onsite', 'Aiden Cooper', 'Technical assessment.', 'available'),
    (10007, '2025-04-18', '09:30:00', 'virtual', 'Liam Adams', 'Final round.', 'available');
