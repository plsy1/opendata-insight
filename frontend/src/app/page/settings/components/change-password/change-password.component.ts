import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { SettingsService } from '../../service/settings.service';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
  ],
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.css'],
})
export class ChangePasswordComponent {
  username: string = 'root';
  oldPassword: string = '';
  newPassword: string = '';
  confirmPassword: string = '';
  message: string = '';
  isLoading: boolean = false;

  constructor(
    private settingsService: SettingsService,
    private snackBar: MatSnackBar
  ) {}

  onChangePassword() {
    this.message = '';

    if (!this.oldPassword || !this.newPassword || !this.confirmPassword) {
      this.snackBar.open(
        'Please fill in all the required information.',
        'Close',
        { duration: 2000 }
      );
      return;
    }

    if (this.newPassword !== this.confirmPassword) {
      this.snackBar.open('The two new passwords do not match.', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
      return;
    }

    this.isLoading = true;

    this.settingsService
      .changePassword(this.username, this.oldPassword, this.newPassword)
      .subscribe({
        next: (success) => {
          if (success) {
            this.snackBar.open('Password changed successfully.', 'Close', {
              duration: 3000,
              panelClass: ['success-snackbar']
            });
            this.oldPassword = '';
            this.newPassword = '';
            this.confirmPassword = '';
          } else {
            this.snackBar.open(
              'Password change failed. Please check your old password.',
              'Close',
              { duration: 2000 }
            );
          }
        },
        error: (err) => {
          console.error('Change password error:', err);
          this.snackBar.open(
            'Password change failed. Please try again later.',
            'Close',
            { duration: 2000 }
          );
        },
        complete: () => {
          this.isLoading = false;
        },
      });
  }
}
