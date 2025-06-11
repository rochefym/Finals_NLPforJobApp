import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-applicant-home',
  standalone: false,
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent {
  activeTab: string = 'resume'; // Set default tab

  setActiveTab(tabName: string): void {
    this.activeTab = tabName;
  }
}
