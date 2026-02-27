import { CommonService } from './../../common.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableDataSource } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
import { MatSort } from '@angular/material/sort';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { DownloadOptionComponent } from './component/download-option/download-option.component';
import { MatDialog } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatIconModule } from '@angular/material/icon';
import { FileSizePipe } from '../../pipe/file-size.pipe';
import { DateFormatPipe } from '../../pipe/date-format.pipe';
import { MatSnackBar } from '@angular/material/snack-bar';
import {
  Component,
  OnInit,
  ViewChild,
  AfterViewInit,
  inject,
} from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TorrentService } from './service/torrent.service';

@Component({
  selector: 'app-torrent-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatSortModule,
    MatFormFieldModule,
    MatInputModule,
    MatTooltipModule,
    MatIconModule,
    FileSizePipe,
    DateFormatPipe,
  ],
  templateUrl: './torrent-list.component.html',
  styleUrl: './torrent-list.component.css',
})
export class TorrentListComponent implements OnInit, AfterViewInit {
  searchResults: any[] = [];
  searchKeyWords: string = '';

  movieId: string = '';
  keywords: string = '';
  dataSource = new MatTableDataSource<any>(this.searchResults);
  dialog: MatDialog = inject(MatDialog);
  @ViewChild(MatSort) sort: MatSort | undefined;
  displayedColumns: string[] = [
    'indexer',
    'title',
    'size',
    'seeders',
    'publishDate',
  ];

  constructor(
    private common: CommonService,
    private getRoute: ActivatedRoute,
    private TorrentService: TorrentService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.getRoute.queryParamMap.subscribe((params) => {
      this.movieId = params.get('fullId') || '';
      this.keywords = params.get('Id') || '';
    });

    this.getRoute.paramMap.subscribe((params) => {
      this.searchKeyWords = params.get('value') || '';
      if (
        this.TorrentService.searchKeyWords === this.searchKeyWords ||
        this.searchKeyWords === ''
      ) {
        this.searchResults = this.TorrentService.searchResults;
        this.dataSource.data = this.searchResults;
      } else {
        this.loadDiscoverData(this.searchKeyWords);
      }
    });

    setTimeout(() => {
      if (this.sort) {
        this.dataSource.sort = this.sort;
        this.sort.active = 'seeders';
        this.sort.direction = 'desc';
      }
    });
  }

  loadDiscoverData(keywords: string): void {
    this.TorrentService.search(keywords).subscribe({
      next: (results: any) => {
        this.searchResults = results;
        this.dataSource.data = this.searchResults;
        this.TorrentService.saveState(this.searchResults, keywords);
        this.snackBar.open('Torrents search completed', 'Close', {
          duration: 3000,
          panelClass: ['success-snackbar'],
        });
      },
      error: (error) => {
        console.error('Failed to load discover data:', error);
      },
    });
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      if (this.sort) {
        this.dataSource.sort = this.sort;
        this.sort.active = 'seeders';
        this.sort.direction = 'desc';
      }
    });
  }

  applyFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value
      .trim()
      .toLowerCase();
    this.dataSource.filter = filterValue;
  }

  onTitleClick(row: any): void {
    const url = row.infoUrl;
    if (url) {
      window.open(url, '_blank');
    }
  }

  onRowClick(row: any): void {
    const downloadUrl = row.magnetUrl || row.downloadUrl;
    const dialogRef = this.dialog.open(DownloadOptionComponent, {
      data: {
        downloadUrl: downloadUrl,
        id: this.movieId,
        keywords: this.keywords,
      },
      panelClass: 'custom-dialog-container'
    });

    row.loading = true;
    row.error = false;
    row.success = false;
    this.dataSource.data = [...this.dataSource.data];

    dialogRef.afterClosed().subscribe((result) => {
      row.loading = false;
      if (result) {
        if (result.success) {
          row.success = true;
          row.error = false;
        } else {
          row.success = false;
          row.error = true;
        }
        this.dataSource.data = [...this.dataSource.data];
      }
    });
  }
}
