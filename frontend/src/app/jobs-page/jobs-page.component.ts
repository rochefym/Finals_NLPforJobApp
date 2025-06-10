import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
    selector: 'app-jobs-page',
    templateUrl: './jobs-page.component.html',
    styleUrls: ['./jobs-page.component.css'],
    standalone: true,
    imports: [CommonModule, FormsModule],
})
export class JobsPageComponent implements OnInit {
    jobs: any[] = [];
    stats: any = {};
    filters = {
        search: '',
        location: '',
        job_type: ''
    };
    jobTypes = ['Full Time', 'Part Time', 'Contract', 'Remote'];

    constructor(private http: HttpClient, private router: Router) { }

    ngOnInit() {
        this.getStats();
        this.getJobs();
    }

    getStats() {
        this.http.get('/api/stats/').subscribe(data => this.stats = data);
    }

    getJobs() {
        let params = new HttpParams();
        if (this.filters.search) params = params.set('search', this.filters.search);
        if (this.filters.location) params = params.set('location', this.filters.location);
        if (this.filters.job_type) params = params.set('job_type', this.filters.job_type);
        this.http.get<any[]>('/api/jobs/', { params }).subscribe(data => this.jobs = data);
    }

    onFilterChange() {
        this.getJobs();
    }

    viewDetails(job: any) {
        this.router.navigate(['/jobs', job.id]);
    }
}
