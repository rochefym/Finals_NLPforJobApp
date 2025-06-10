import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router'; // Import RouterLink
import { AuthService } from '../auth.service';
import { FormsModule } from '@angular/forms'; // Import FormsModule
import { CommonModule } from '@angular/common'; // Import CommonModule

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink], // Add FormsModule, CommonModule, RouterLink
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  name = '';
  email = '';
  password = '';
  confirmPassword = '';
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  passwordsMismatch = false;

  constructor(private authService: AuthService, private router: Router) { }

  checkPasswords(password: string, confirmPassword_val: string) {
    this.passwordsMismatch = password !== confirmPassword_val;
  }

  async onSubmit() {
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    if (this.password !== this.confirmPassword) {
      this.errorMessage = 'Passwords do not match.';
      this.isLoading = false;
      return;
    }

    try {
      const success = await this.authService.register({
        name: this.name,
        email: this.email,
        password: this.password
      });
      if (success) {
        this.successMessage = 'Registration successful! You can now login.';
        // Optionally, redirect to login or automatically log in
        // this.router.navigate(['/login']); 
      } else {
        this.errorMessage = 'Registration failed. Please try again.';
      }
    } catch (error) {
      this.errorMessage = 'An error occurred during registration.';
      console.error('Registration error', error);
    }
    this.isLoading = false;
  }
}
