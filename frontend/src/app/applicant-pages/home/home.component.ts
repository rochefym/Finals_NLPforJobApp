import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-applicant-home',
  standalone: false,
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent {
  selectedFile!: File;
  fileName: any;
  applicantId: number = 1;  // set this dynamically or statically as needed

  constructor(private http: HttpClient) {}    

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
    this.fileName = this.selectedFile.name.split('.')[0]; 
  }

  upload() {
    if (!this.selectedFile) return;

    const formData = new FormData();
    formData.append('applicant', this.applicantId.toString());
    formData.append('name', this.fileName);
    formData.append('pdf_file', this.selectedFile);

    this.http.post('http://localhost:8000/api/resume/', formData).subscribe({
      next: (res) => console.log('Upload success', res),
      error: (err) => console.error('Upload failed', err),
    });
  }
  
}
