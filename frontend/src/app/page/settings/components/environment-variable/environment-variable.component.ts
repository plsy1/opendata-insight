import { Component, OnInit } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { EnvironmentConfig } from '../../models/settings.interface';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { SettingsService } from '../../service/settings.service';
@Component({
  selector: 'app-environment-variable',
  standalone: true,
  imports: [
    CommonModule,
    TranslateModule,
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
  ],
  templateUrl: './environment-variable.component.html',
  styleUrl: './environment-variable.component.css',
})
export class EnvironmentVariableComponent implements OnInit {
  constructor(
    private SettingsService: SettingsService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.SettingsService.getEnvironment().subscribe({
      next: (data: EnvironmentConfig) => {
        this.env = data;
      },
      error: (error) => {},
    });
  }

  env: EnvironmentConfig = {
    PROWLARR_URL: '',
    PROWLARR_KEY: '',
    DOWNLOAD_PATH: '',
    QB_URL: '',
    QB_PORT: '',
    QB_USERNAME: '',
    QB_PASSWORD: '',
    QB_KEYWORD_FILTER: [],
    TELEGRAM_TOKEN: '',
    TELEGRAM_CHAT_ID: '',
    EMBY_URL: '',
    EMBY_API_KEY: '',
  };

saveEnv() {
  this.SettingsService.updateEnvironment(this.env).subscribe({
    next: (success: boolean) => {
      if (success) {
        this.snackBar.open('Saved successfully.', 'Close', { 
          duration: 3000,
          panelClass: ['success-snackbar']
        });
      } else {
        this.snackBar.open('Failed. Please try again.', 'Close', { 
          duration: 3000,
          panelClass: ['error-snackbar']
        });
      }
    },
    error: (error) => {
      console.error('Error saving environment:', error);
      this.snackBar.open('Failed. Please try again.', 'Close', { duration: 2000 });
    },
  });
}
}
