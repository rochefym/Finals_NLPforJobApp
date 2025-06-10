import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { marked } from 'marked';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

interface JobPrediction {
  0: string;
  1: number;
}

interface AnalysisData {
  name: string;
  email: string;
  mobile_number: string;
  years_of_experience: string;
  experience_level: string;
  experience_range: string;
  experience_description: string;
  skills: string[];
  educational_institutions: string[];
  educational_attainment: string[];
  no_of_pages: number;
  predicted_job_categories: JobPrediction[];
  recommended_jobs: JobPrediction[];
  timestamp: string;
}

@Component({
  selector: 'app-resume',
  standalone: false,
  templateUrl: './resume.component.html',
  styleUrl: './resume.component.css'
})
export class ResumeComponent {
  selectedFile!: File;
  fileName: any;
  applicantId: number = 1;

  isLoading = false;
  errorMessage = '';

  analysisData: AnalysisData | null = null;
  result_1: any;
  result_2: any;
  marked_up_result_2: SafeHtml = '';

  constructor(
    private http: HttpClient,
    private sanitizer: DomSanitizer
  ) {
    marked.setOptions({
      breaks: true,
      gfm: true,
    });
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
    this.fileName = this.selectedFile.name.split('.')[0]; 
  }

  upload() {
    this.isLoading = true;
    if (!this.selectedFile) return;

    const formData = new FormData();
    formData.append('applicant', this.applicantId.toString());
    formData.append('name', this.fileName);
    formData.append('pdf_file', this.selectedFile);

    this.http.post('http://localhost:8000/api/resume/', formData).subscribe({
      next: (res) => {
        console.log('Upload success', res);
        this.result_1 = res;
        this.analysisData = this.result_1.analysis;
        this.getResumeAnalysis();
      },
      error: (err) => {
        console.error('Upload failed', err);
        this.isLoading = false;
      },
    });
  }

  async getResumeAnalysis() {
    try {
      const res = await this.http.get(`http://localhost:8000/api/applicant/${this.applicantId}/resume/`).toPromise();
      console.log('Success. Analysis of RESUME: ', res);
      this.result_2 = res;
      
      const contentToParse = typeof this.result_2 === 'string' 
        ? this.result_2 
        : JSON.stringify(this.result_2);
      
      // Await the marked.parse() call
      const parsedMarkdown = await marked.parse(contentToParse);
      this.marked_up_result_2 = this.sanitizer.bypassSecurityTrustHtml(parsedMarkdown);
      
    } catch (err) {
      console.error('Analysis fetch failed', err);
    } finally {
      this.isLoading = false;
    }
  }
}