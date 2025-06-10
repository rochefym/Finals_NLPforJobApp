import { Injectable } from '@angular/core';
import { BehaviorSubject, lastValueFrom } from 'rxjs'; // Import lastValueFrom
import { HttpClient, HttpErrorResponse } from '@angular/common/http'; // Import HttpClient and HttpErrorResponse

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // BehaviorSubject to hold the current authentication state
  private loggedIn = new BehaviorSubject<boolean>(false); // Initially, user is not logged in
  isLoggedIn$ = this.loggedIn.asObservable(); // Expose as observable

  constructor(private http: HttpClient) { // Inject HttpClient
    // Check for a token in localStorage to maintain session across reloads
    const token = localStorage.getItem('authToken');
    if (token) {
      this.loggedIn.next(true);
    }
  }

  // Placeholder for login logic
  login(email: string, password: string): Promise<boolean> {
    // In a real app, you'd make an HTTP request to your backend here
    // For now, simulate a successful login and store a dummy token
    return new Promise((resolve) => {
      setTimeout(() => {
        localStorage.setItem('authToken', 'dummyToken'); // Store a dummy token
        this.loggedIn.next(true);
        resolve(true);
      }, 1000);
    });
  }

  // Placeholder for registration logic
  async register(userData: any): Promise<boolean> {
    try {
      // Assuming the current registration is for an Applicant
      // Adjust the endpoint if you have separate employer registration flow on frontend
      await lastValueFrom(this.http.post('/api/register/applicant/', userData));
      // Optionally, log the user in directly after registration if your backend returns a token
      // Or simply return true and let the user log in manually
      return true;
    } catch (error) {
      console.error('Registration failed', error);
      // You can inspect error to provide more specific feedback
      // For example, if it's an HttpErrorResponse and error.status === 400,
      // it might be due to duplicate email or validation errors from backend.
      return false;
    }
  }

  logout(): void {
    localStorage.removeItem('authToken'); // Remove the token
    this.loggedIn.next(false);
    // Optionally, navigate to login page or home page
    // this.router.navigate(['/login']);
  }

  isAuthenticated(): boolean {
    return this.loggedIn.value;
  }
}
