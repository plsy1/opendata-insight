import { TranslateModule } from '@ngx-translate/core';
import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { CommonService } from '../../../../common.service';

import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-search-option',
  standalone: true,
  imports: [
    MatFormFieldModule,
    MatInputModule,
    FormsModule,
    MatSelectModule,
    CommonModule,
    MatAutocompleteModule,
    MatButtonToggleModule,
    MatDialogModule,
    MatIconModule,
    TranslateModule,
  ],
  templateUrl: './search-option.component.html',
  styleUrl: './search-option.component.css',
})
export class SearchOptionComponent {
  searchType: string = '';
  searchVaule: string = '';
  searchKeywordsOptions: string[] = [];
  filteredOptions: string[] = [];

  constructor(
    private dialogRef: MatDialogRef<SearchOptionComponent>,
    private snackBar: MatSnackBar,
    private router: Router,
    private common: CommonService,
    @Inject(MAT_DIALOG_DATA) public data: { title: string; type: string }
  ) {
    this.filteredOptions = this.searchKeywordsOptions;
  }
  ngOnInit(): void {
    const savedPaths = localStorage.getItem('searchKeywordsOptions');
    if (savedPaths) {
      this.searchKeywordsOptions = JSON.parse(savedPaths);
      this.filteredOptions = [...this.searchKeywordsOptions];
    }
  }

  async searchTorrents(): Promise<void> {
    try {
      this.common.isJumpFromProductionPage = false;
      this.snackBar.open('Searching......', 'Close', { 
        duration: 2000,
        panelClass: ['info-snackbar']
      });
      this.router.navigate(['/torrents', this.searchVaule]);
      this.setRecentlySearch();
    } catch (error) {
      this.snackBar.open('Failed. Please try again.', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
    } finally {
      this.dialogRef.close();
    }
  }

  async searchPerformer(): Promise<void> {
    try {
      this.snackBar.open('Searching......', 'Close', { 
        duration: 2000,
        panelClass: ['info-snackbar']
      });
      this.router.navigate([`/performer/${this.searchVaule}`]);
      this.setRecentlySearch();
    } catch (error) {
      this.snackBar.open('Failed. Please try again.', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
    } finally {
      this.dialogRef.close();
    }
  }

  async searchKeywords(): Promise<void> {
    try {
      this.snackBar.open('Searching......', 'Close', { 
        duration: 2000,
        panelClass: ['info-snackbar']
      });
      this.router.navigate([`/keywords/${this.searchVaule}`]);
      this.setRecentlySearch();
    } catch (error) {
      this.snackBar.open('Failed. Please try again.', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
    } finally {
      this.dialogRef.close();
    }
  }

  setRecentlySearch() {
    if (
      this.searchVaule &&
      !this.searchKeywordsOptions.includes(this.searchVaule)
    ) {
      this.searchKeywordsOptions.unshift(this.searchVaule); // Use unshift to add to front

      localStorage.setItem(
        'searchKeywordsOptions',
        JSON.stringify(this.searchKeywordsOptions)
      );

      this.filteredOptions = [...this.searchKeywordsOptions];
    }
  }

  removeRecentSearch(option: string, event: Event) {
    event.stopPropagation(); // Prevent triggering the search
    this.searchKeywordsOptions = this.searchKeywordsOptions.filter(
      (o) => o !== option
    );
    this.filteredOptions = [...this.searchKeywordsOptions];
    localStorage.setItem(
      'searchKeywordsOptions',
      JSON.stringify(this.searchKeywordsOptions)
    );
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
