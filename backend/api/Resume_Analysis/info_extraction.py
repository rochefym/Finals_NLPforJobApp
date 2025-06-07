import re
import spacy
import os
from pdfminer.high_level import extract_text
from PyPDF2 import PdfReader
from nltk.tokenize import sent_tokenize

# List of predefined skills
skills_list = [
    # Communication & Interpersonal
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
    
    # Technical Skills
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
    'Content Management Systems (CMS)', 'WordPress', 'Joomla', 'Drupal', 'Magento', 'Shopify', 'E-commerce',
    'Payment Gateways', 'Inventory Management', 'Supply Chain Management', 'Logistics', 'Procurement', 'ERP Systems', 'SAP', 'Oracle',
    'Microsoft Dynamics', 'Power BI', 'QlikView', 'Looker', 'Data Engineering', 'Data Governance',
    'Data Quality', 'Master Data Management', 'Predictive Analytics', 'Prescriptive Analytics', 'Descriptive Analytics', 'Business Intelligence',
    'Dashboarding', 'Reporting', 'Data Mining', 'Web Scraping', 'API Integration', 'RESTful APIs', 'GraphQL', 'SOAP', 'Microservices',
    'Serverless Architecture', 'Lambda Functions', 'Event-Driven Architecture', 'Message Queues', 'Socket.io', 'WebSockets',
    'Ruby', 'Ruby on Rails', 'PHP', 'Symfony', 'Laravel', 'CakePHP', 'Zend Framework', 'ASP.NET', 'C#', 'VB.NET', 'ASP.NET MVC', 'Entity Framework',
    'Spring', 'Hibernate', 'Struts', 'Kotlin', 'Swift', 'Objective-C', 'iOS Development', 'Android Development', 'Flutter', 'React Native', 'Ionic',
    'Mobile UI/UX Design', 'Material Design', 'SwiftUI', 'RxJava', 'RxSwift', 'Django', 'Flask', 'FastAPI', 'Falcon', 'Tornado',
    'Server Administration', 'System Administration', 'Network Administration', 'Database Administration', 'MySQL', 'PostgreSQL',
    'SQLite', 'Microsoft SQL Server', 'Oracle Database', 'NoSQL', 'Cassandra', 'Redis', 'Elasticsearch', 'Firebase',
    'Google Tag Manager', 'Adobe Analytics', 'Marketing Automation', 'Customer Data Platforms', 'Segment', 'Salesforce Marketing Cloud', 'HubSpot CRM',
    'Zapier', 'IFTTT', 'Workflow Automation', 'Robotic Process Automation (RPA)', 'UI Automation', 'Natural Language Generation (NLG)',
    'Virtual Reality (VR)', 'Augmented Reality (AR)', 'Mixed Reality (MR)', 'Unity', 'Unreal Engine', '3D Modeling', 'Animation', 'Motion Graphics',
    'Game Design', 'Game Development', 'Level Design', 'Unity3D', 'Unreal Engine 4', 'Blender', 'Maya', 'Adobe After Effects', 'Adobe Premiere Pro',
    'Final Cut Pro', 'Video Editing', 'Audio Editing', 'Sound Design', 'Music Production', 'Digital Marketing', 'Content Strategy', 'Conversion Rate Optimization (CRO)',
    'A/B Testing', 'Customer Experience (CX)', 'User Interface (UI)', 'Persona Development', 'User Journey Mapping', 'Information Architecture (IA)',
    'Internationalization (I18n)', 'Voice User Interface (VUI)',
    'Chatbots', 'Natural Language Understanding (NLU)', 'Speech Synthesis', 'Emotion Detection', 'Sentiment Analysis', 'Image Recognition', 'Object Detection',
    'Facial Recognition', 'Gesture Recognition', 'Document Recognition', 'Fraud Detection', 'Cyber Threat Intelligence', 'Security Information and Event Management (SIEM)',
    'Vulnerability Assessment', 'Incident Response', 'Forensic Analysis', 'Security Operations Center (SOC)', 'Identity and Access Management (IAM)', 'Single Sign-On (SSO)',
    'Multi-Factor Authentication (MFA)', 'Blockchain', 'Cryptocurrency', 'Decentralized Finance (DeFi)', 'Smart Contracts', 'Web3', 'Non-Fungible Tokens (NFTs)'
]

education_keywords = [
    # Computer & Technology Fields
    'Computer Science', 'Computer Engineering', 'Software Engineering', 'Information Technology',
    'Data Science', 'Artificial Intelligence', 'Cybersecurity', 'Information Systems',
    'Computer Networks', 'Web Development', 'Game Development', 'Mobile Development',
    'Cloud Computing', 'Blockchain Technology', 'Robotics', 'Mechatronics',
    
    # Engineering Fields
    'Electrical Engineering', 'Electronics Engineering', 'Mechanical Engineering', 'Civil Engineering',
    'Chemical Engineering', 'Biomedical Engineering', 'Aerospace Engineering', 'Industrial Engineering',
    'Environmental Engineering', 'Petroleum Engineering', 'Nuclear Engineering', 'Automotive Engineering',
    'Systems Engineering', 'Marine Engineering', 'Geological Engineering',
    
    # Business & Management Fields
    'Business Administration', 'Business Management', 'Entrepreneurship', 'Finance', 'Accounting',
    'Economics', 'Marketing', 'Human Resource Management', 'Supply Chain Management', 'Logistics',
    'International Business', 'Hospitality Management', 'Tourism Management', 'Project Management',
    'Operations Management', 'Strategic Management', 'Public Administration', 'Organizational Behavior',
    'Quality Management', 'Risk Management',
    
    # Mathematics & Sciences
    'Mathematics', 'Applied Mathematics', 'Statistics', 'Physics', 'Chemistry', 'Biology',
    'Biotechnology', 'Biochemistry', 'Microbiology', 'Genetics', 'Neuroscience', 'Geology',
    'Astronomy', 'Meteorology', 'Environmental Science', 'Marine Biology', 'Molecular Biology',
    'Bioinformatics', 'Biophysics', 'Biostatistics',
    
    # Health & Medicine
    'Medicine', 'Dentistry', 'Pharmacy', 'Nursing', 'Public Health', 'Veterinary Medicine',
    'Physiotherapy', 'Occupational Therapy', 'Nutrition', 'Sports Science', 'Psychology',
    'Clinical Research', 'Epidemiology', 'Physical Therapy', 'Speech Therapy', 'Kinesiology',
    'Exercise Physiology', 'Sports Medicine', 'Rehabilitation Science', 'Medical Technology',
    'Radiography', 'Pharmacology', 'Physiology', 'Anatomy', 'Pathology', 'Immunology',
    
    # Arts & Humanities
    'English Literature', 'History', 'Philosophy', 'Linguistics', 'Journalism', 'Communication',
    'Political Science', 'International Relations', 'Sociology', 'Anthropology', 'Archaeology',
    'Fine Arts', 'Graphic Design', 'Film Studies', 'Music', 'Theater Arts', 'Creative Writing',
    'Visual Arts', 'Fashion Design', 'Industrial Design', 'Interior Design', 'Animation',
    'Media Studies', 'Communication Studies', 'Broadcasting', 'Translation Studies',
    'Foreign Languages', 'Modern Languages', 'Classical Studies', 'Theology', 'Religious Studies',
    'Ethics',
    
    # Education Fields
    'Education', 'Early Childhood Education', 'Elementary Education', 'Secondary Education',
    'Special Education', 'Educational Technology', 'Curriculum Development', 'Adult Education',
    'Higher Education', 'Distance Education', 'Online Education', 'Instructional Design',
    
    # Law & Criminal Justice
    'Law', 'Criminal Justice', 'Criminology', 'Forensic Science', 'Legal Studies',
    'Crime Scene Investigation', 'Emergency Management', 'Fire Science',
    
    # Architecture & Design
    'Architecture', 'Interior Design', 'Landscape Architecture', 'Urban Planning',
    'Fashion Design', 'Industrial Design', 'Product Design',
    
    # Vocational & Technical
    'Culinary Arts', 'Automotive Technology', 'Aviation', 'Construction Management',
    'Electrical Technology', 'Welding Technology',
    
    # Other Sciences
    'Geography', 'Geomatics', 'Remote Sensing', 'Geoinformatics', 'Cartography', 
    'GIS (Geographic Information Systems)', 'Environmental Management', 'Sustainability Studies', 
    'Renewable Energy', 'Green Technology', 'Ecology', 'Conservation Biology', 'Wildlife Biology', 
    'Zoology', 'Climate Science', 'Library Science', 'Information Science',
    
    # Certifications & Degrees
    'Bachelor', 'Master', 'PhD', 'Doctorate', 'MBA', 'MS', 'BS', 'BSc', 'MSc',
    'Diploma', 'Certificate', 'Associate Degree', 'Professional Certification'
]

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

class InformationExtraction:
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            return extract_text(pdf_path)
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_email(self, text):
        """Extract email address from text"""
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else None

    def extract_mobile(self, text):
        """Extract mobile number from text"""
        # More comprehensive phone number pattern
        patterns = [
            r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,5}[-.\s]?\d{4,5}',
            r'\+\d{1,3}\s?\d{3,4}\s?\d{3,4}\s?\d{3,4}',
            r'\(\d{3}\)\s?\d{3}-?\d{4}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    def extract_name(self, text):
        """Extract name using NLP"""
        try:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text
        except Exception as e:
            print(f"Error extracting name: {e}")
        return ""
    
    def extract_skills(self, text):
        """Extract skills from text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in skills_list:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(found_skills))

    def extract_experience(self, text):
        y_match = re.search(r'(\d+)\s+year', text.lower())
        m_match = re.search(r'(\d+)\s+month', text.lower())
        years = int(y_match.group(1)) if y_match else 0
        months = int(m_match.group(1)) if m_match else 0
        total = round(years + months / 12, 2)
        return total

    def extract_college(self, text):
        """Extract college/university names"""
        lines = text.split('\n')
        colleges = []
        
        college_keywords = ['college', 'university', 'institute', 'school', 'academy']
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in college_keywords):
                colleges.append(line)
        
        return colleges

    def extract_degree(self, text):
        """Extract degree information"""
        text_lower = text.lower()
        found_degrees = []
        
        for degree in education_keywords:
            if degree.lower() in text_lower:
                found_degrees.append(degree)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(found_degrees))

    def get_pdf_page_count(self, filepath):
        """Get number of pages in PDF"""
        try:
            reader = PdfReader(filepath)
            return len(reader.pages)
        except Exception as e:
            print(f"Error counting PDF pages: {e}")
            return 0

    def parse_resume(self, pdf_path):
        """Main function to parse resume and extract all information"""
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
            return None
        
        try:
            text = self.extract_text_from_pdf(pdf_path)
            
            if not text:
                print("No text extracted from PDF")
                return None
            
            return {
                'name': self.extract_name(text),
                'email': self.extract_email(text),
                'mobile_number': self.extract_mobile(text),
                'skills': self.extract_skills(text),
                'total_experience': self.extract_experience(text),
                'educational_institutions': self.extract_college(text),
                'degree': self.extract_degree(text),
                'no_of_pages': self.get_pdf_page_count(pdf_path)
            }
            
        except Exception as e:
            print(f"Error parsing resume: {e}")
            return None


# Example usage
if __name__ == "__main__":
    # Update this path to your actual PDF file
    pdf_abs_path = r'C:\Users\rochefym\Documents\Finals_NLPforJobApp\I_resume_parser_files\Uploaded_Resumes\data-scientist-1559725114.pdf'
    
    # Process the resume
    if os.path.exists(pdf_abs_path):
        extractor = InformationExtraction()
        output = extractor.parse_resume(pdf_abs_path)
        print(output.get('name'))

        if output:
            print("Resume parsing successful!")
            for key, value in output.items():
                print(f"{key}: {value}")
        else:
            print("Failed to parse resume")
    else:
        print("File not found. Please verify the path:")
        print(pdf_abs_path)