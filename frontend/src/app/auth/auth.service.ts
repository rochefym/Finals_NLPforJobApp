import { Injectable } from '@angular/core';
import { BehaviorSubject, lastValueFrom, Observable } from 'rxjs';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router'; // Import Router

// Define an interface for the login response
interface LoginResponse {
  access: string;
  refresh: string;
  user_id: number;
  user_type: 'applicant' | 'employer';
  email: string;
  name: string;
}

// Define an interface for stored user data
interface StoredUser {
  id: number;
  email: string;
  name: string;
  userType: 'applicant' | 'employer';
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private loggedIn = new BehaviorSubject<boolean>(false);
  isLoggedIn$: Observable<boolean> = this.loggedIn.asObservable();
  private currentUser = new BehaviorSubject<StoredUser | null>(null);
  currentUser$: Observable<StoredUser | null> = this.currentUser.asObservable();


  constructor(private http: HttpClient, private router: Router) { // Inject Router
    this.loadCurrentUser();
  }

  private loadCurrentUser(): void {
    const accessToken = localStorage.getItem('accessToken');
    const user = localStorage.getItem('currentUser');
    if (accessToken && user) {
      this.loggedIn.next(true);
      this.currentUser.next(JSON.parse(user));
    } else {
      this.loggedIn.next(false);
      this.currentUser.next(null);
    }
  }

  async login(email: string, password: string): Promise<boolean> {
    try {
      const response = await lastValueFrom(this.http.post<LoginResponse>('/api/login/', { email, password }));
      if (response && response.access) {
        localStorage.setItem('accessToken', response.access);
        localStorage.setItem('refreshToken', response.refresh);
        const userData: StoredUser = {
          id: response.user_id,
          email: response.email,
          name: response.name,
          userType: response.user_type
        };
        localStorage.setItem('currentUser', JSON.stringify(userData));
        this.loggedIn.next(true);
        this.currentUser.next(userData);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login failed', error);
      this.loggedIn.next(false);
      this.currentUser.next(null);
      return false;
    }
  }

  async register(userData: any): Promise<boolean> {
    try {
      // Assuming the current registration is for an Applicant
      // Adjust the endpoint if you have separate employer registration flow on frontend
      // Consider what the backend returns upon successful registration.
      // If it returns login tokens, you can log the user in directly.
      await lastValueFrom(this.http.post('/api/register/applicant/', userData));
      // For now, we assume registration is successful and user needs to login separately.
      return true;
    } catch (error) {
      console.error('Registration failed', error);
      return false;
    }
  }

  logout(): void {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('currentUser');
    this.loggedIn.next(false);
    this.currentUser.next(null);
    this.router.navigate(['/login']); // Navigate to login page after logout
  }

  isAuthenticated(): boolean {
    return this.loggedIn.value;
  }

  getCurrentUser(): StoredUser | null {
    return this.currentUser.value;
  }

  getAccessToken(): string | null {
    return localStorage.getItem('accessToken');
  }

  // Optional: Add a method to refresh the token if your backend supports it
  // async refreshToken(): Promise<boolean> {
  //   const refreshToken = localStorage.getItem('refreshToken');
  //   if (!refreshToken) {
  //     this.logout(); // No refresh token, logout
  //     return false;
  //   }
  //   try {
  //     const response = await lastValueFrom(this.http.post<{ access: string }>('/api/token/refresh/', { refresh: refreshToken }));
  //     if (response && response.access) {
  //       localStorage.setItem('accessToken', response.access);
  //       this.loggedIn.next(true); // Ensure loggedIn state is updated if it was false
  //       return true;
  //     }
  //     this.logout(); // Failed to refresh, logout
  //     return false;
  //   } catch (error) {
  //     console.error('Token refresh failed', error);
  //     this.logout(); // Error during refresh, logout
  //     return false;
  //   }
  // }
}
