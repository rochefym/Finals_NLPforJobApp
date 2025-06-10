import { Component } from '@angular/core';
import { Router, ActivatedRoute, RouterLink } from '@angular/router'; // Import RouterLink
import { AuthService } from '../auth.service';
import { FormsModule } from '@angular/forms'; // Import FormsModule
import { CommonModule } from '@angular/common'; // Import CommonModule

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink], // Add FormsModule, CommonModule, RouterLink
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  email = '';
  password = '';
  isLoading = false;
  errorMessage = '';
  private returnUrl = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    // Get the return URL from the query parameters or default to '/'
    this.route.queryParams.subscribe(params => {
      this.returnUrl = params['returnUrl'] || '/';
    });
  }

  async onSubmit() {
    this.isLoading = true;
    this.errorMessage = '';
    try {
      const success = await this.authService.login(this.email, this.password);
      if (success) {
        this.router.navigate([this.returnUrl]);
      } else {
        this.errorMessage = 'Login failed. Please check your credentials.';
      }
    } catch (error) {
      this.errorMessage = 'An error occurred during login.';
      console.error('Login error', error);
    }
    this.isLoading = false;
  }
}
