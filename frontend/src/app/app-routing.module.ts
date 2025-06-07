import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './applicant-pages/home/home.component';
import { ResumeComponent } from './applicant-pages/resume/resume.component';

const routes: Routes = [
  { path: '', component: HomeComponent }, // Default route
  // { path: '', component: ResumeComponent, pathMatch: 'full' }, 
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
