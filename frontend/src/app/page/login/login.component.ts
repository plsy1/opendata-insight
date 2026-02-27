import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { CommonService } from '../../common.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    MatInputModule,
    MatButtonModule,
    MatFormFieldModule,
    MatCardModule,
    MatIconModule,
    FormsModule,
    CommonModule,
    TranslateModule,
  ],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
})
export class LoginComponent {
  username: string = '';
  password: string = '';

  constructor(
    private router: Router,
    private common: CommonService,
    private snackbar: MatSnackBar,
    private translate: TranslateService
  ) {}

  ngOnInit(): void {
    if (localStorage.getItem('loggedIn') === 'true') {
      this.router.navigate(['']);
    }
  }

onSubmit(): void {
  this.common.login(this.username, this.password).subscribe({
    next: (success) => {
      if (success) {
        localStorage.setItem('username', this.username);
        this.router.navigate(['']);
      } else {
        this.translate.get('LOGIN.ERROR').subscribe(msg => this.showErrorSnackbar(msg));
      }
    },
    error: (error) => {
      console.error('Login request failed:', error);
      this.translate.get('LOGIN.ERROR').subscribe(msg => this.showErrorSnackbar(msg));
    }
  });
}

  private showErrorSnackbar(message: string) {
    this.snackbar.open(message, 'Close', {
      duration: 3000,
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
      panelClass: ['error-snackbar'],
    });
  }
}
