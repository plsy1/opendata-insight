import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CommonModule } from '@angular/common';
import {
  DownloadMediaType,
  TorrentService,
} from '../../service/torrent.service';
import { SettingsService } from '../../../settings/service/settings.service';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatOptionModule } from '@angular/material/core';
import { lastValueFrom } from 'rxjs';
import { MatIcon } from '@angular/material/icon';

@Component({
  selector: 'app-download-option',
  templateUrl: './download-option.component.html',
  styleUrl: './download-option.component.css',
  standalone: true,
  imports: [
    MatFormFieldModule,
    MatInputModule,
    FormsModule,
    MatSelectModule,
    CommonModule,
    MatAutocompleteModule,
    MatOptionModule,
    MatIcon,
    TranslateModule
  ],
})
export class DownloadOptionComponent {
  downloadUrl: string;
  savePathOptions: string[] = [];
  savePath: string = '';
  filteredOptions: string[] = [];
  workId: string = '';
  mediaType?: DownloadMediaType;
  defaultPathHintKey = 'SETTINGS.DEFAULT_DOWNLOAD_PATH_HINT';

  constructor(
    private dialogRef: MatDialogRef<DownloadOptionComponent>,
    private snackBar: MatSnackBar,
    private torrentService: TorrentService,
    private settingsService: SettingsService,
    private translate: TranslateService,
    @Inject(MAT_DIALOG_DATA)
    public data: {
      downloadUrl: string;
      workId: string;
      mediaType?: DownloadMediaType;
    }
  ) {
    this.downloadUrl = data.downloadUrl;
    this.filteredOptions = this.savePathOptions;
    this.workId = data.workId;
    this.mediaType = data.mediaType;
    this.defaultPathHintKey =
      this.mediaType === 'fc2'
        ? 'TORRENTS.FC2_DEFAULT_PATH_HINT'
        : this.mediaType === 'jav'
          ? 'TORRENTS.JAV_DEFAULT_PATH_HINT'
          : 'SETTINGS.DEFAULT_DOWNLOAD_PATH_HINT';
  }

  ngOnInit(): void {
    const savedPaths = localStorage.getItem('savePathOptions');
    if (savedPaths) {
      try {
        const parsedPaths = JSON.parse(savedPaths);
        this.savePathOptions = Array.isArray(parsedPaths) ? parsedPaths : [];
      } catch {
        this.savePathOptions = [];
      }
    }
    this.filteredOptions = [...this.savePathOptions];

    this.settingsService.getEnvironment().subscribe({
      next: (env) => {
        const mediaPath =
          this.mediaType === 'fc2'
            ? env.FC2_DOWNLOAD_PATH
            : this.mediaType === 'jav'
              ? env.JAV_DOWNLOAD_PATH
              : '';
        this.savePath = mediaPath || env.DOWNLOAD_PATH || '';
        if (this.savePath && !this.savePathOptions.includes(this.savePath)) {
          this.savePathOptions.unshift(this.savePath);
        }
        this.filteredOptions = [...this.savePathOptions];
      },
      error: (error) => {
        console.error('Failed to load default download path:', error);
      },
    });
  }

  async download(): Promise<void> {
    try {
      this.snackBar.open(this.translate.instant('TORRENTS.SENDING'), this.translate.instant('COMMON.CLOSE'), { 
        duration: 2000,
        panelClass: ['info-snackbar']
      });

      await lastValueFrom(
        this.torrentService.pushTorrent(
          this.workId,
          this.downloadUrl,
          this.savePath,
          this.mediaType
        )
      );

      if (this.savePath && !this.savePathOptions.includes(this.savePath)) {
        this.savePathOptions.push(this.savePath);
        localStorage.setItem(
          'savePathOptions',
          JSON.stringify(this.savePathOptions)
        );
        this.filteredOptions = [...this.savePathOptions];
      }

      this.dialogRef.close({
        success: true,
        message: this.translate.instant('TORRENTS.DOWNLOAD_STARTED'),
      });
    } catch (error) {
      console.error('Send failed:', error);

      this.dialogRef.close({
        success: false,
        message: this.translate.instant('TORRENTS.DOWNLOAD_FAILED'),
      });
      this.snackBar.open(this.translate.instant('TORRENTS.DOWNLOAD_FAILED'), this.translate.instant('COMMON.CLOSE'), {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
    }
  }

  close() {
    this.dialogRef.close();
  }

  showErrorNotification(message: string) {
    this.snackBar.open(message, this.translate.instant('COMMON.CLOSE'), {
      duration: 3000,
      panelClass: ['error-snackbar'],
    });
  }
}
