import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './applicant-pages/home/home.component';
import { JobsPageComponent } from './jobs-page/jobs-page.component';
import { ResumeComponent } from './applicant-pages/resume/resume.component';
import { JobDetailComponent } from './jobs-page/job-detail.component';
import { LoginComponent } from './auth/login/login.component'; // Add import for LoginComponent
import { RegisterComponent } from './auth/register/register.component'; // Add import for RegisterComponent

export const routes: Routes = [
  { path: '', component: HomeComponent }, // Default route
  { path: 'jobs', component: JobsPageComponent }, // Jobs page
  { path: 'jobs/:id', component: JobDetailComponent }, // Job details page
  { path: 'resume', component: ResumeComponent }, // Resume upload page
  { path: 'login', component: LoginComponent }, // Login page route
  { path: 'register', component: RegisterComponent }, // Register page route
  { path: '**', redirectTo: '' } // Wildcard route should be last
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
