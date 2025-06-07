from PyPDF2 import PdfReader
import re
import pickle
import os


# -------------------------------LOAD Trained Models------------------------------------
# Get the directory of the current file (Resume_Analysis/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths to model and vectorizer inside models/
RF_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'rf_classifier_categorization.pkl')
TFIDF_PATH = os.path.join(BASE_DIR, 'models', 'tfidf_vectorizer_categorization.pkl')

RF_MODEL_PATH_2 = os.path.join(BASE_DIR, 'models', 'rf_classifier_job_recommendation.pkl')
TFIDF_PATH_2 = os.path.join(BASE_DIR, 'models', 'tfidf_vectorizer_job_recommendation.pkl')

# JOB FIELD CATEGORIZATION: Load the classifier and vectorizer
with open(RF_MODEL_PATH, 'rb') as rf_file:
    rf_classifier_categorization = pickle.load(rf_file)

with open(TFIDF_PATH, 'rb') as tfidf_file:
    tfidf_vectorizer_categorization = pickle.load(tfidf_file)

#JOB FIELD RECOMENDATION
with open(RF_MODEL_PATH_2, 'rb') as rf_file:
    rf_classifier_job_recommendation = pickle.load(rf_file)

with open(TFIDF_PATH_2, 'rb') as tfidf_file:
    tfidf_vectorizer_job_recommendation  = pickle.load(tfidf_file)


# -------------------------------INFORMATION EXTRACTION------------------------------------


    
#--------------------------------RESUME ANALYSIS-------------------------------------------
class ResumeAnalysis:

    def clean_resume(self, text):
        # Remove URLs starting with http (e.g., http://example.com)
        cleanText = re.sub(r'http/S+\s', ' ', text)

        # Remove common retweet and copy-paste tags (often seen in social media text)
        cleanText = re.sub(r'RT|cc', ' ', cleanText)

        # Remove hashtags and the word following them (e.g., #Python)
        cleanText = re.sub(r'#\S+\s', ' ', cleanText)

        # Remove mentions like @username
        cleanText = re.sub(r'@\S+', ' ', cleanText)

        # Remove punctuation and special characters using escaped characters
        cleanText = re.sub('[%s]' % re.escape(r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', cleanText)

        # Remove non-ASCII characters (e.g., emojis, foreign scripts)
        cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText)

        # Replace multiple spaces, tabs, and newlines with a single space
        cleanText = re.sub(r'\s+', ' ', cleanText)

        # Return the cleaned text
        return cleanText



    def pdf_to_text(self, pdf_file):
        reader = PdfReader(pdf_file)
        text = ''
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
        return text
    

    def predict_field_category(self, cleaned_resume_text):
        resume_tfidf = tfidf_vectorizer_categorization.transform([cleaned_resume_text])
        predicted_field_category = rf_classifier_categorization.predict(resume_tfidf)[0]

        return predicted_field_category
    

    def recommend_job(self, cleaned_resume_text):
        resume_tfidf = tfidf_vectorizer_job_recommendation.transform([cleaned_resume_text])
        recommended_job = rf_classifier_job_recommendation.predict(resume_tfidf)[0]
        
        return recommended_job


    def get_resume_analysis(self, pdf_file):
        if(pdf_file):
            # 1. Convert resume pdf_file to text
            resume_text = self.pdf_to_text(pdf_file)

            # 2. Preprocess text; Remove unecessary patterns (punctuations, hashtags, urls/links, etc); Use REs
            cleaned_resume_text = self.clean_resume(resume_text)

            # 3. Predict Category/Field
            predicted_field_category = self.predict_field_category(cleaned_resume_text)

            # 4. Recommend Job Category/Field
            recommended_job = self.recommend_job(cleaned_resume_text)

            return predicted_field_category, recommended_job


import re
import spacy
import dateparser
from pdfminer.high_level import extract_text
from nltk.tokenize import sent_tokenize


# List of predefined skills
skills_list = [# Communication & Interpersonal
    "Active Listening", "Storytelling", "Nonverbal Communication", "Cross-Cultural Communication",
    "Persuasion", "Negotiation", "Public Relations", "Networking", "Diplomacy", "Mediation",
    
    # Leadership & Management
    "Team Building", "Delegation", "Coaching", "Mentoring", "Change Management", "Crisis Management",
    "Stakeholder Management", "Performance Evaluation", "Strategic Leadership", "People Management",
    
    # Problem-Solving & Critical Thinking
    "Analytical Reasoning", "Logical Thinking", "Creativity", "Innovation", "Troubleshooting",
    "Root Cause Analysis", "Decision-Making", "Research Skills", "Attention to Detail", "Systems Thinking",
    
    # Work Ethic & Professionalism
    "Reliability", "Punctuality", "Adaptability", "Work-Life Balance", "Professional Development",
    "Continuous Learning", "Self-Motivation", "Integrity", "Accountability", "Resilience",
    
    # Collaboration & Teamwork
    "Conflict Resolution", "Consensus Building", "Group Facilitation", "Interdepartmental Coordination",
    "Peer Support", "Team Motivation", "Collaborative Problem-Solving", "Remote Teamwork",
    "Virtual Collaboration", "Inclusivity",
    
    # Organization & Productivity
    "Task Prioritization", "Goal Setting", "Deadline Management", "Workflow Optimization",
    "Process Improvement", "Lean Methodology", "Agile Mindset", "Meeting Management",
    "Documentation", "Administrative Skills",
    
    # Customer & Client Focus
    "Customer Relationship Management (CRM)", "Client Retention", "Customer Success",
    "User Experience (UX) Research", "Feedback Collection", "Complaint Resolution",
    "Hospitality", "Service Excellence", "B2B Communication", "B2C Engagement",
    
    # Digital & Remote Work
    "Virtual Communication", "Online Collaboration Tools", "Digital Etiquette",
    "Cybersecurity Awareness", "Remote Project Management", "Cloud-Based Workflows",
    "Asynchronous Communication", "Digital Note-Taking", "Online Research", "Data Privacy Knowledge",
    
    # Financial & Business Acumen
    "Budget Management", "Cost-Benefit Analysis", "Financial Literacy", "Business Writing",
    "Market Analysis", "Competitive Intelligence", "ROI Calculation", "Procurement",
    "Vendor Management", "Contract Negotiation",
    
    # Personal Development
    "Growth Mindset", "Self-Discipline", "Stress Management", "Emotional Intelligence (EQ)",
    "Mindfulness", "Time Blocking", "Habit Formation", "Career Planning", "Personal Branding",
    "Lifelong Learning",
    
    # Creativity & Design Thinking
    "Brainstorming", "Ideation", "Visual Thinking", "Design Sprints", "Prototyping",
    "User-Centered Design", "Aesthetic Sensibility", "Storyboarding", "Concept Development",
    "Artistic Expression",
    
    # Language & Writing
    "Proofreading", "Editing", "Technical Documentation", "Grant Writing", "Business Proposals",
    "Report Writing", "Copy Editing", "Localization", "Multilingual Proficiency", "Translation",
    'Python', 'Data Analysis', 'Machine Learning', 'Communication', 'Project Management', 'Deep Learning', 'SQL', 'Tableau',
    'Java', 'C++', 'JavaScript', 'HTML', 'CSS', 'React', 'Angular', 'Node.js', 'MongoDB', 'Express.js', 'Git',
    'Research', 'Statistics', 'Quantitative Analysis', 'Qualitative Analysis', 'SPSS', 'R', 'Data Visualization', 'Matplotlib',
    'Seaborn', 'Plotly', 'Pandas', 'Numpy', 'Scikit-learn', 'TensorFlow', 'Keras', 'PyTorch', 'NLTK', 'Text Mining',
    'Natural Language Processing', 'Computer Vision', 'Image Processing', 'OCR', 'Speech Recognition', 'Recommendation Systems',
    'Collaborative Filtering', 'Content-Based Filtering', 'Reinforcement Learning', 'Neural Networks', 'Convolutional Neural Networks',
    'Recurrent Neural Networks', 'Generative Adversarial Networks', 'XGBoost', 'Random Forest', 'Decision Trees', 'Support Vector Machines',
    'Linear Regression', 'Logistic Regression', 'K-Means Clustering', 'Hierarchical Clustering', 'DBSCAN', 'Association Rule Learning',
    'Apache Hadoop', 'Apache Spark', 'MapReduce', 'Hive', 'HBase', 'Apache Kafka', 'Data Warehousing', 'ETL', 'Big Data Analytics',
    'Cloud Computing', 'Amazon Web Services (AWS)', 'Microsoft Azure', 'Google Cloud Platform (GCP)', 'Docker', 'Kubernetes', 'Linux',
    'Shell Scripting', 'Cybersecurity', 'Network Security', 'Penetration Testing', 'Firewalls', 'Encryption', 'Malware Analysis',
    'Digital Forensics', 'CI/CD', 'DevOps', 'Agile Methodology', 'Scrum', 'Kanban', 'Continuous Integration', 'Continuous Deployment',
    'Software Development', 'Web Development', 'Mobile Development', 'Backend Development', 'Frontend Development', 'Full-Stack Development',
    'UI/UX Design', 'Responsive Design', 'Wireframing', 'Prototyping', 'User Testing', 'Adobe Creative Suite', 'Photoshop', 'Illustrator',
    'InDesign', 'Figma', 'Sketch', 'Zeplin', 'InVision', 'Product Management', 'Market Research', 'Customer Development', 'Lean Startup',
    'Business Development', 'Sales', 'Marketing', 'Content Marketing', 'Social Media Marketing', 'Email Marketing', 'SEO', 'SEM', 'PPC',
    'Google Analytics', 'Facebook Ads', 'LinkedIn Ads', 'Lead Generation', 'Customer Relationship Management (CRM)', 'Salesforce',
    'HubSpot', 'Zendesk', 'Intercom', 'Customer Support', 'Technical Support', 'Troubleshooting', 'Ticketing Systems', 'ServiceNow',
    'ITIL', 'Quality Assurance', 'Manual Testing', 'Automated Testing', 'Selenium', 'JUnit', 'Load Testing', 'Performance Testing',
    'Regression Testing', 'Black Box Testing', 'White Box Testing', 'API Testing', 'Mobile Testing', 'Usability Testing', 'Accessibility Testing',
    'Cross-Browser Testing', 'Agile Testing', 'User Acceptance Testing', 'Software Documentation', 'Technical Writing', 'Copywriting',
    'Editing', 'Proofreading', 'Content Management Systems (CMS)', 'WordPress', 'Joomla', 'Drupal', 'Magento', 'Shopify', 'E-commerce',
    'Payment Gateways', 'Inventory Management', 'Supply Chain Management', 'Logistics', 'Procurement', 'ERP Systems', 'SAP', 'Oracle',
    'Microsoft Dynamics', 'Tableau', 'Power BI', 'QlikView', 'Looker', 'Data Warehousing', 'ETL', 'Data Engineering', 'Data Governance',
    'Data Quality', 'Master Data Management', 'Predictive Analytics', 'Prescriptive Analytics', 'Descriptive Analytics', 'Business Intelligence',
    'Dashboarding', 'Reporting', 'Data Mining', 'Web Scraping', 'API Integration', 'RESTful APIs', 'GraphQL', 'SOAP', 'Microservices',
    'Serverless Architecture', 'Lambda Functions', 'Event-Driven Architecture', 'Message Queues', 'GraphQL', 'Socket.io', 'WebSockets'
'Ruby', 'Ruby on Rails', 'PHP', 'Symfony', 'Laravel', 'CakePHP', 'Zend Framework', 'ASP.NET', 'C#', 'VB.NET', 'ASP.NET MVC', 'Entity Framework',
    'Spring', 'Hibernate', 'Struts', 'Kotlin', 'Swift', 'Objective-C', 'iOS Development', 'Android Development', 'Flutter', 'React Native', 'Ionic',
    'Mobile UI/UX Design', 'Material Design', 'SwiftUI', 'RxJava', 'RxSwift', 'Django', 'Flask', 'FastAPI', 'Falcon', 'Tornado', 'WebSockets',
    'GraphQL', 'RESTful Web Services', 'SOAP', 'Microservices Architecture', 'Serverless Computing', 'AWS Lambda', 'Google Cloud Functions',
    'Azure Functions', 'Server Administration', 'System Administration', 'Network Administration', 'Database Administration', 'MySQL', 'PostgreSQL',
    'SQLite', 'Microsoft SQL Server', 'Oracle Database', 'NoSQL', 'MongoDB', 'Cassandra', 'Redis', 'Elasticsearch', 'Firebase', 'Google Analytics',
    'Google Tag Manager', 'Adobe Analytics', 'Marketing Automation', 'Customer Data Platforms', 'Segment', 'Salesforce Marketing Cloud', 'HubSpot CRM',
    'Zapier', 'IFTTT', 'Workflow Automation', 'Robotic Process Automation (RPA)', 'UI Automation', 'Natural Language Generation (NLG)',
    'Virtual Reality (VR)', 'Augmented Reality (AR)', 'Mixed Reality (MR)', 'Unity', 'Unreal Engine', '3D Modeling', 'Animation', 'Motion Graphics',
    'Game Design', 'Game Development', 'Level Design', 'Unity3D', 'Unreal Engine 4', 'Blender', 'Maya', 'Adobe After Effects', 'Adobe Premiere Pro',
    'Final Cut Pro', 'Video Editing', 'Audio Editing', 'Sound Design', 'Music Production', 'Digital Marketing', 'Content Strategy', 'Conversion Rate Optimization (CRO)',
    'A/B Testing', 'Customer Experience (CX)', 'User Experience (UX)', 'User Interface (UI)', 'Persona Development', 'User Journey Mapping', 'Information Architecture (IA)',
    'Wireframing', 'Prototyping', 'Usability Testing', 'Accessibility Compliance', 'Internationalization (I18n)', 'Localization (L10n)', 'Voice User Interface (VUI)',
    'Chatbots', 'Natural Language Understanding (NLU)', 'Speech Synthesis', 'Emotion Detection', 'Sentiment Analysis', 'Image Recognition', 'Object Detection',
    'Facial Recognition', 'Gesture Recognition', 'Document Recognition', 'Fraud Detection', 'Cyber Threat Intelligence', 'Security Information and Event Management (SIEM)',
    'Vulnerability Assessment', 'Incident Response', 'Forensic Analysis', 'Security Operations Center (SOC)', 'Identity and Access Management (IAM)', 'Single Sign-On (SSO)',
    'Multi-Factor Authentication (MFA)', 'Blockchain', 'Cryptocurrency', 'Decentralized Finance (DeFi)', 'Smart Contracts', 'Web3', 'Non-Fungible Tokens (NFTs)']

education_keywords = [
        'Computer Science', 'Information Technology', 'Software Engineering', 'Electrical Engineering', 'Mechanical Engineering', 'Civil Engineering',
        'Chemical Engineering', 'Biomedical Engineering', 'Aerospace Engineering', 'Nuclear Engineering', 'Industrial Engineering', 'Systems Engineering',
        'Environmental Engineering', 'Petroleum Engineering', 'Geological Engineering', 'Marine Engineering', 'Robotics Engineering', 'Biotechnology',
        'Biochemistry', 'Microbiology', 'Genetics', 'Molecular Biology', 'Bioinformatics', 'Neuroscience', 'Biophysics', 'Biostatistics', 'Pharmacology',
        'Physiology', 'Anatomy', 'Pathology', 'Immunology', 'Epidemiology', 'Public Health', 'Health Administration', 'Nursing', 'Medicine', 'Dentistry',
        'Pharmacy', 'Veterinary Medicine', 'Medical Technology', 'Radiography', 'Physical Therapy', 'Occupational Therapy', 'Speech Therapy', 'Nutrition',
        'Sports Science', 'Kinesiology', 'Exercise Physiology', 'Sports Medicine', 'Rehabilitation Science', 'Psychology', 'Counseling', 'Social Work',
        'Sociology', 'Anthropology', 'Criminal Justice', 'Political Science', 'International Relations', 'Economics', 'Finance', 'Accounting', 'Business Administration',
        'Management', 'Marketing', 'Entrepreneurship', 'Hospitality Management', 'Tourism Management', 'Supply Chain Management', 'Logistics Management',
        'Operations Management', 'Human Resource Management', 'Organizational Behavior', 'Project Management', 'Quality Management', 'Risk Management',
        'Strategic Management', 'Public Administration', 'Urban Planning', 'Architecture', 'Interior Design', 'Landscape Architecture', 'Fine Arts',
        'Visual Arts', 'Graphic Design', 'Fashion Design', 'Industrial Design', 'Product Design', 'Animation', 'Film Studies', 'Media Studies',
        'Communication Studies', 'Journalism', 'Broadcasting', 'Creative Writing', 'English Literature', 'Linguistics', 'Translation Studies',
        'Foreign Languages', 'Modern Languages', 'Classical Studies', 'History', 'Archaeology', 'Philosophy', 'Theology', 'Religious Studies',
        'Ethics', 'Education', 'Early Childhood Education', 'Elementary Education', 'Secondary Education', 'Special Education', 'Higher Education',
        'Adult Education', 'Distance Education', 'Online Education', 'Instructional Design', 'Curriculum Development'
        'Library Science', 'Information Science', 'Computer Engineering', 'Software Development', 'Cybersecurity', 'Information Security',
        'Network Engineering', 'Data Science', 'Data Analytics', 'Business Analytics', 'Operations Research', 'Decision Sciences',
        'Human-Computer Interaction', 'User Experience Design', 'User Interface Design', 'Digital Marketing', 'Content Strategy',
        'Brand Management', 'Public Relations', 'Corporate Communications', 'Media Production', 'Digital Media', 'Web Development',
        'Mobile App Development', 'Game Development', 'Virtual Reality', 'Augmented Reality', 'Blockchain Technology', 'Cryptocurrency',
        'Digital Forensics', 'Forensic Science', 'Criminalistics', 'Crime Scene Investigation', 'Emergency Management', 'Fire Science',
        'Environmental Science', 'Climate Science', 'Meteorology', 'Geography', 'Geomatics', 'Remote Sensing', 'Geoinformatics',
        'Cartography', 'GIS (Geographic Information Systems)', 'Environmental Management', 'Sustainability Studies', 'Renewable Energy',
        'Green Technology', 'Ecology', 'Conservation Biology', 'Wildlife Biology', 'Zoology', # Computer & Technology Fields
    'Computer Science', 'Computer Engineering', 'Software Engineering', 'Information Technology',
    'Data Science', 'Artificial Intelligence', 'Cybersecurity', 'Information Systems',
    'Computer Networks', 'Web Development', 'Game Development', 'Mobile Development',
    'Cloud Computing', 'Blockchain Technology', 'Robotics', 'Mechatronics',
    
    # Engineering Fields
    'Electrical Engineering', 'Electronics Engineering', 'Mechanical Engineering', 'Civil Engineering',
    'Chemical Engineering', 'Biomedical Engineering', 'Aerospace Engineering', 'Industrial Engineering',
    'Environmental Engineering', 'Petroleum Engineering', 'Nuclear Engineering', 'Automotive Engineering',
    
    # Business & Management Fields
    'Business Administration', 'Business Management', 'Entrepreneurship', 'Finance', 'Accounting',
    'Economics', 'Marketing', 'Human Resource Management', 'Supply Chain Management', 'Logistics',
    'International Business', 'Hospitality Management', 'Tourism Management', 'Project Management',
    
    # Mathematics & Sciences
    'Mathematics', 'Applied Mathematics', 'Statistics', 'Physics', 'Chemistry', 'Biology',
    'Biotechnology', 'Biochemistry', 'Microbiology', 'Genetics', 'Neuroscience', 'Geology',
    'Astronomy', 'Meteorology', 'Environmental Science', 'Marine Biology',
    
    # Health & Medicine
    'Medicine', 'Dentistry', 'Pharmacy', 'Nursing', 'Public Health', 'Veterinary Medicine',
    'Physiotherapy', 'Occupational Therapy', 'Nutrition', 'Sports Science', 'Psychology',
    'Clinical Research', 'Epidemiology',
    
    # Arts & Humanities
    'English Literature', 'History', 'Philosophy', 'Linguistics', 'Journalism', 'Communication',
    'Political Science', 'International Relations', 'Sociology', 'Anthropology', 'Archaeology',
    'Fine Arts', 'Graphic Design', 'Film Studies', 'Music', 'Theater Arts', 'Creative Writing',
    
    # Education Fields
    'Education', 'Early Childhood Education', 'Elementary Education', 'Secondary Education',
    'Special Education', 'Educational Technology', 'Curriculum Development', 'Adult Education',
    
    # Law & Criminal Justice
    'Law', 'Criminal Justice', 'Criminology', 'Forensic Science', 'Legal Studies',
    
    # Architecture & Design
    'Architecture', 'Interior Design', 'Landscape Architecture', 'Urban Planning',
    'Fashion Design', 'Industrial Design',
    
    # Vocational & Technical
    'Culinary Arts', 'Automotive Technology', 'Aviation', 'Construction Management',
    'Electrical Technology', 'Welding Technology',
    
    # Certifications & Degrees
    'Bachelor', 'Master', 'PhD', 'Doctorate', 'MBA', 'MS', 'BS', 'BSc', 'MSc',
    'Diploma', 'Certificate', 'Associate Degree', 'Professional Certification']

nlp = spacy.load("en_core_web_sm")

class InformationExtraction:

    def extract_text_from_pdf(self, pdf_path):
        return extract_text(pdf_path)
    
    # Extract Contact Info
    def extract_email(self, text):
        match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        return match.group(0) if match else None

    def extract_mobile(self, text):
        match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,5}[-.\s]?\d{4,5}', text)
        return match.group(0) if match else None

    def extract_name(self, text):
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return ""
    
    def extract_skills(self, text):
        text_lower = text.lower()
        found_skills = []
        for skill in skills_list:
            if skill in text_lower:
                found_skills.append(skill)
        return found_skills

    def extract_experience(self, text):
        y_match = re.search(r'(\d+)\s+year', text.lower())
        m_match = re.search(r'(\d+)\s+month', text.lower())
        years = int(y_match.group(1)) if y_match else 0
        months = int(m_match.group(1)) if m_match else 0
        total = round(years + months / 12, 2)
        return total

    def extract_college(self, text):
        lines = text.split('\n')
        return [line.strip() for line in lines if "college" in line.lower()]

    def extract_degree(self, text):
        text_lower = text.lower()
        return [deg for deg in education_keywords if deg in text_lower]
    

    def get_pdf_page_count(self, filepath):
        reader = PdfReader(filepath)
        return len(reader.pages)


    # Combine all into one function
    def parse_resume(self, pdf_path):
        text = self.extract_text_from_pdf(pdf_path)

        return {
            'name': self.extract_name(text),
            'email': self.extract_email(text),
            'mobile_number': self.extract_mobile(text),
            'skills': self.extract_skills(text),
            'total_experience': self.extract_experience(text),
            'college_name': self.extract_college(text),
            'degree': self.extract_degree(text),
            'no_of_pages': self.get_pdf_page_count(pdf_path)
        }

    

    


# extractor = InformationExtraction()
# output = extractor.parse_resume('Uploaded_Resumes/android-developer-1559034496.pdf')
# print(output)

# Absolute path to your PDF
pdf_abs_path = r'C:\Users\rochefym\Documents\Finals_NLPforJobApp\I_resume_parser_files\Uploaded_Resumes\android-developer-1559034496.pdf'

# Process the resume
if os.path.exists(pdf_abs_path):
    extractor = InformationExtraction()
    output = extractor.parse_resume(pdf_abs_path)
    print(output)
else:
    print("File not found. Please verify:")
    print(pdf_abs_path)
