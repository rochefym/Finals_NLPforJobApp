import os
from dotenv import load_dotenv
from groq import Groq
from pdfminer.high_level import extract_text


load_dotenv()

class ResumeAnalysis:
    # Grok 
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Function to extract text from PDF
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            return extract_text(pdf_path)
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""



    # Function to get response from Groq AI
    def analyze_resume(self, resume_pdf, job_description=None):
        resume_text = self.extract_text_from_pdf(resume_pdf)

        if not resume_text:
            return {"error": "Resume text is required for analysis."}
        
        base_prompt = f"""
        You are an experienced HR with Technical Experience in the field of any job roles. Your task is to review the provided resume.
        Please share your professional evaluation on whether the candidate's profile aligns with the role. Also mention Skills he already have and suggest some skills to improve his resume, also suggest some course he might take to improve the skills. Highlight the strengths and weaknesses.
        Don't mention yourself and stay in the context that the one prompting is the one in the resume.

        Resume:
        {resume_text}
        """
        
        if job_description:
            base_prompt += f"""
            Additionally, compare this resume to the following job description:
            Job Description: {job_description}
            
            Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
            """
        
        try:
            completion = self.client.chat.completions.create(
                model="compound-beta", 
                messages=[{"role": "user", "content": base_prompt}],
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False
            )
            
            analysis = completion.choices[0].message.content
            return analysis
        
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
        


# resume = r'C:\Users\rochefym\Documents\Finals_NLPforJobApp\backend\media\pdfs\android-developer-1559034496.pdf'
# resume_analyser = ResumeAnalysis()

# analysis = resume_analyser.analyze_resume(resume)

# print(analysis)

