import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CommonModule } from '@angular/common';
import { TorrentService } from '../../service/torrent.service';
import { CommonService } from '../../../../common.service';
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
    MatOptionModule,MatIcon
  ],
})
export class DownloadOptionComponent {
  downloadUrl: string;
  savePathOptions: string[] = [];
  savePath: string = '';
  filteredOptions: string[] = [];
  id: string = '';
  keywords: string = '';

  constructor(
    private dialogRef: MatDialogRef<DownloadOptionComponent>,
    private snackBar: MatSnackBar,
    private torrentService: TorrentService,
    private common: CommonService,
    @Inject(MAT_DIALOG_DATA)
    public data: { downloadUrl: string; id: string; keywords: string }
  ) {
    this.downloadUrl = data.downloadUrl;
    this.filteredOptions = this.savePathOptions;
    this.id = data.id;
    this.keywords = data.keywords;
  }

  ngOnInit(): void {
    const savedPaths = localStorage.getItem('savePathOptions');
    if (savedPaths) {
      this.savePathOptions = JSON.parse(savedPaths);
      this.filteredOptions = [...this.savePathOptions];
    }
  }

  async download(): Promise<void> {
    try {
      this.snackBar.open('Sending......', 'Close', { 
        duration: 2000,
        panelClass: ['info-snackbar']
      });

        const name = this.common.isJumpFromProductionPage
        ? this.common.currentPerformer
        : '';


      const results = await lastValueFrom(
        this.torrentService.pushTorrent(
          this.keywords,
          this.id,
          this.downloadUrl,
          this.savePath,
          name
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
        message: 'Download started successfully!',
      });
    } catch (error) {
      console.error('Send failed:', error);

      this.dialogRef.close({
        success: false,
        message: 'Failed. Please try again.',
      });
      this.snackBar.open('Failed. Please try again.', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
    }
  }

  close() {
    this.dialogRef.close();
  }

  showErrorNotification(message: string) {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      panelClass: ['error-snackbar'],
    });
  }
}
