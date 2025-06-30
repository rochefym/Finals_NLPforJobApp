import { Component } from '@angular/core';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { AuthService } from '../auth.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http'; // Import HttpErrorResponse

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  name = '';
  email = '';
  phone_number = ''; // Add phone_number property
  password = '';
  confirmPassword = '';
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  passwordsMismatch = false;
  private returnUrl = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.route.queryParams.subscribe(params => {
      this.returnUrl = params['returnUrl'] || '/jobs';
    });
  }

  checkPasswords(password: string, confirmPassword_val: string) {
    this.passwordsMismatch = password !== confirmPassword_val;
  }

  async onSubmit() {
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    if (this.password !== this.confirmPassword) {
      this.errorMessage = 'Passwords do not match.';
      this.passwordsMismatch = true;
      this.isLoading = false;
      return;
    }
    this.passwordsMismatch = false;

    try {
      const registrationSuccess = await this.authService.register({
        name: this.name,
        email: this.email,
        phone_number: this.phone_number, // Use the bound phone_number property
        password: this.password,
      });

      if (registrationSuccess) {
        this.successMessage = 'Registration successful! Attempting to log you in...';
        const loginSuccess = await this.authService.login(this.email, this.password);
        if (loginSuccess) {
          this.router.navigate([this.returnUrl]);
        } else {
          this.errorMessage = 'Registration was successful, but auto-login failed. Please try logging in manually.';
          this.router.navigate(['/login'], { queryParams: { returnUrl: this.returnUrl } });
        }
      } else {
        this.errorMessage = 'Registration failed. Please try again. The email might already be in use or the data is invalid.';
      }
    } catch (error: any) {
      if (error instanceof HttpErrorResponse) {
        // Check for backend validation errors (e.g., duplicate email)
        if (error.status === 400 && error.error) {
          if (error.error.email) {
            this.errorMessage = `Email error: ${error.error.email.join(', ')}`;
          } else if (error.error.password) {
            this.errorMessage = `Password error: ${error.error.password.join(', ')}`;
          } else if (typeof error.error === 'string') {
            this.errorMessage = error.error; // Generic error string from backend
          } else {
            this.errorMessage = 'Registration failed due to validation errors.';
          }
        } else {
          this.errorMessage = error.error?.detail || 'An error occurred during registration.';
        }
      } else {
        this.errorMessage = 'An unexpected error occurred during registration.';
      }
      console.error('Registration error', error);
    }
    this.isLoading = false;
  }
}
