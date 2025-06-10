import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../auth/auth.service';

@Component({
    selector: 'app-job-detail',
    templateUrl: './job-detail.component.html',
    styleUrls: ['./job-detail.component.css'],
    standalone: true,
    imports: [CommonModule, FormsModule],
})
export class JobDetailComponent implements OnInit {
    job: any = null;
    similarJobs: any[] = [];

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
            // User is logged in, open application modal logic here
            console.log('User is authenticated, opening application modal...');
            // TODO: Implement modal opening logic
        } else {
            // User is not logged in, redirect to login page
            this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
        }
    }
}
