import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { JobMatcherComponent } from './applicant-pages/job-matcher/job-matcher.component';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
// Angular Material Modules
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTabsModule } from '@angular/material/tabs';
import { MatCardModule } from '@angular/material/card';
import { ProfileComponent } from './applicant-pages/profile/profile.component';
import { JobsPageComponent } from './jobs-page/jobs-page.component';
import { JobDetailComponent } from './jobs-page/job-detail.component';
import { HomeComponent } from './applicant-pages/home/home.component';

@NgModule({
  declarations: [
    AppComponent,
    JobMatcherComponent,
    ProfileComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatTabsModule,
    MatCardModule,
    HttpClientModule,
    FormsModule,
    JobsPageComponent,
    JobDetailComponent,
    HomeComponent
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
