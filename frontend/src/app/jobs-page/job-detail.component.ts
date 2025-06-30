import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router'; // Import RouterLink
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../auth/auth.service';

interface ApplicationForm {
    name: string;
    email: string;
    phone_number: string;
    start_date: string; // YYYY-MM-DD
    resume_file: File | null;
    years_of_experience: number | null;
    expected_salary: number | null;
    cover_letter: string;
}

@Component({
    selector: 'app-job-detail',
    templateUrl: './job-detail.component.html',
    styleUrls: ['./job-detail.component.css'],
    standalone: true,
    imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterLink], // Add RouterLink here
})
export class JobDetailComponent implements OnInit {
    job: any = null;
    similarJobs: any[] = [];
    showApplicationModal = false;
    applicationForm: ApplicationForm = {
        name: '',
        email: '',
        phone_number: '',
        start_date: '',
        resume_file: null,
        years_of_experience: null,
        expected_salary: null,
        cover_letter: ''
    };
    applicationSubmitting = false;
    applicationSuccessMessage = '';
    applicationErrorMessage = '';
    selectedResumeFile: File | null = null;

    constructor(
        private route: ActivatedRoute,
        private http: HttpClient,
        private authService: AuthService,
        private router: Router
    ) { }

    ngOnInit() {
        const id = this.route.snapshot.paramMap.get('id');
        this.http.get(`/api/jobs/${id}/`).subscribe(data => {
            this.job = data;
            this.loadSimilarJobs();
        });

        // Pre-fill form if user is logged in
        if (this.authService.isAuthenticated()) {
            const currentUser = this.authService.getCurrentUser();
            if (currentUser) {
                this.applicationForm.name = currentUser.name;
                this.applicationForm.email = currentUser.email;
            }
        }
    }

    loadSimilarJobs() {
        if (!this.job) return;
        this.http.get<any[]>(`/api/jobs/`, {
            params: { job_type: this.job.work_type, location: this.job.location }
        }).subscribe(jobs => {
            this.similarJobs = jobs.filter(j => j.id !== this.job.id).slice(0, 3);
        });
    }

    applyNow() {
        if (this.authService.isAuthenticated()) {
            this.openApplicationModal();
        } else {
            this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
        }
    }

    openApplicationModal() {
        this.applicationSuccessMessage = '';
        this.applicationErrorMessage = '';
        this.selectedResumeFile = null;
        // Reset form fields but keep pre-filled name and email if user is logged in
        const currentUser = this.authService.getCurrentUser();
        this.applicationForm = {
            name: currentUser?.name || '',
            email: currentUser?.email || '',
            phone_number: '',
            start_date: '',
            resume_file: null,
            years_of_experience: null,
            expected_salary: null,
            cover_letter: ''
        };
        this.showApplicationModal = true;
    }

    closeApplicationModal() {
        this.showApplicationModal = false;
    }

    onFileSelected(event: Event): void {
        const element = event.currentTarget as HTMLInputElement;
        let fileList: FileList | null = element.files;
        if (fileList && fileList.length > 0) {
            this.selectedResumeFile = fileList[0];
            this.applicationForm.resume_file = this.selectedResumeFile; // Keep for direct form data if needed
        }
    }

    submitApplication() {
        if (!this.selectedResumeFile) {
            this.applicationErrorMessage = 'Please select a resume file.';
            return;
        }
        if (!this.job || !this.job.id) {
            this.applicationErrorMessage = 'Job ID is missing. Cannot submit application.';
            return;
        }

        this.applicationSubmitting = true;
        this.applicationSuccessMessage = '';
        this.applicationErrorMessage = '';

        const formData = new FormData();
        formData.append('name', this.applicationForm.name);
        formData.append('email', this.applicationForm.email);
        formData.append('phone_number', this.applicationForm.phone_number);
        formData.append('start_date', this.applicationForm.start_date);
        formData.append('years_of_experience', this.applicationForm.years_of_experience?.toString() || '0');
        formData.append('expected_salary', this.applicationForm.expected_salary?.toString() || '0');
        formData.append('cover_letter', this.applicationForm.cover_letter);
        if (this.selectedResumeFile) {
            formData.append('resume_file', this.selectedResumeFile, this.selectedResumeFile.name);
        }

        // Note: The backend ApplyToJobView expects these fields.
        // Ensure your backend view matches this payload.

        const headers = new HttpHeaders({
            // 'Content-Type': 'multipart/form-data' // HttpClient sets this automatically for FormData
            // Add Authorization header if your API requires it for this endpoint
            'Authorization': `Bearer ${this.authService.getAccessToken()}`
        });

        this.http.post(`/api/jobs/${this.job.id}/apply/`, formData, { headers })
            .subscribe({
                next: (response: any) => {
                    this.applicationSubmitting = false;
                    this.applicationSuccessMessage = response.message || 'Application submitted successfully!';
                    // Optionally close modal after a delay or keep it open to show success
                    setTimeout(() => this.closeApplicationModal(), 3000);
                },
                error: (error) => {
                    this.applicationSubmitting = false;
                    if (error.error && typeof error.error === 'object') {
                        // Try to extract specific error messages
                        let messages = [];
                        for (const key in error.error) {
                            if (Array.isArray(error.error[key])) {
                                messages.push(`${key}: ${error.error[key].join(', ')}`);
                            }
                        }
                        this.applicationErrorMessage = messages.length > 0 ? messages.join('; ') : (error.error.detail || 'Failed to submit application. Please try again.');
                    } else if (error.error && typeof error.error === 'string') {
                        this.applicationErrorMessage = error.error;
                    } else {
                        this.applicationErrorMessage = 'Failed to submit application. Please check your input and try again.';
                    }
                    console.error('Application submission error', error);
                }
            });
    }
}
