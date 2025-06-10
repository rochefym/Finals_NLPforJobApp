import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common'; // Added CommonModule
import { HeaderComponent } from '../../components/header/header.component'; // Added HeaderComponent import
import { ResumeComponent } from '../resume/resume.component'; // Added ResumeComponent import

@Component({
  selector: 'app-home', // Changed selector to 'app-home'
  standalone: true, // Changed to standalone: true
  imports: [CommonModule, HeaderComponent, ResumeComponent], // Added imports
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent {


}
