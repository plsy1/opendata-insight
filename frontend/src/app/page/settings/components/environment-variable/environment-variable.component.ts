import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateModule } from '@ngx-translate/core';
import { EnvironmentConfig } from '../../models/settings.interface';
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
  env: EnvironmentConfig = {
    PROWLARR_URL: '',
    PROWLARR_KEY: '',
    DOWNLOAD_PATH: '',
    JAV_DOWNLOAD_PATH: '',
    FC2_DOWNLOAD_PATH: '',
    QB_URL: '',
    QB_USERNAME: '',
    QB_PASSWORD: '',
    QB_KEYWORD_FILTER: [],
    SUBSCRIBE_GLOBAL_EXCLUDED: [],
    SUBSCRIBE_QUALITY_RULES: [],
    TELEGRAM_TOKEN: '',
    TELEGRAM_CHAT_ID: '',
    EMBY_URL: '',
    EMBY_API_KEY: '',
  };

  constructor(
    private settingsService: SettingsService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.settingsService.getEnvironment().subscribe({
      next: (data: EnvironmentConfig) => {
        this.env = data;
      },
      error: (error) => {
        console.error('Error loading environment:', error);
      },
    });
  }

  saveEnv(): void {
    const {
      SUBSCRIBE_GLOBAL_EXCLUDED: _globalExcluded,
      SUBSCRIBE_QUALITY_RULES: _qualityRules,
      ...payload
    } = this.env;

    this.settingsService.updateEnvironment(payload).subscribe({
      next: (success: boolean) => {
        if (success) {
          this.snackBar.open('Saved successfully.', 'Close', {
            duration: 3000,
            panelClass: ['success-snackbar'],
          });
        } else {
          this.showSaveError();
        }
      },
      error: (error) => {
        console.error('Error saving environment:', error);
        this.showSaveError();
      },
    });
  }

  private showSaveError(): void {
    this.snackBar.open('Failed. Please try again.', 'Close', {
      duration: 3000,
      panelClass: ['error-snackbar'],
    });
  }
}
