import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
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
import {
  DownloadMediaType,
  TorrentService,
} from './service/torrent.service';
import { TorrentSearchResult } from './models/torrent-search-result.interface';

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
    MatIconModule,
    FileSizePipe,
    DateFormatPipe,
    TranslateModule,
    MatTooltipModule
  ],
  templateUrl: './torrent-list.component.html',
  styleUrl: './torrent-list.component.css',
})
export class TorrentListComponent implements OnInit, AfterViewInit {
  searchResults: TorrentSearchResult[] = [];
  searchKeyWords: string = '';

  workId: string = '';
  mediaType?: DownloadMediaType;
  dataSource = new MatTableDataSource<TorrentSearchResult>(this.searchResults);
  dialog: MatDialog = inject(MatDialog);
  @ViewChild(MatSort) sort: MatSort | undefined;
  displayedColumns: string[] = [
    'indexer',
    'title',
    'technical',
    'size',
    'seeders',
    'publishDate',
  ];

  constructor(
    private getRoute: ActivatedRoute,
    private TorrentService: TorrentService,
    private snackBar: MatSnackBar,
    private translate: TranslateService
  ) {}

  ngOnInit(): void {
    this.getRoute.queryParamMap.subscribe((params) => {
      // `Id` was used by older links; keep it as a read-only fallback.
      this.workId = params.get('workId') || params.get('Id') || '';
      const mediaType = params.get('mediaType');
      this.mediaType =
        mediaType === 'jav' || mediaType === 'fc2' ? mediaType : undefined;
    });

    this.getRoute.paramMap.subscribe((params) => {
      this.searchKeyWords = params.get('query') || '';
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
      next: (results) => {
        this.searchResults = results;
        this.dataSource.data = this.searchResults;
        if (this.sort) {
          this.sort.active = 'seeders';
          this.sort.direction = 'desc';
          this.sort.sortChange.emit({ active: 'seeders', direction: 'desc' });
        }
        this.TorrentService.saveState(this.searchResults, keywords);
        this.snackBar.open(
          this.translate.instant('TORRENTS.SEARCH_COMPLETED'),
          this.translate.instant('COMMON.CLOSE'),
          {
            duration: 3000,
            panelClass: ['success-snackbar'],
          }
        );
      },
      error: (error) => {
        console.error('Failed to load discover data:', error);
      },
    });
  }

  ngAfterViewInit(): void {
    if (this.sort) {
      this.dataSource.sort = this.sort;
      this.sort.active = 'seeders';
      this.sort.direction = 'desc';
      this.sort.sortChange.emit({ active: 'seeders', direction: 'desc' });
    }
  }

  applyFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value
      .trim()
      .toLowerCase();
    this.dataSource.filter = filterValue;
  }

  codecLabel(codec: string | null | undefined): string {
    const labels: Record<string, string> = {
      av1: 'AV1',
      h265: 'H.265',
      h264: 'H.264',
      vp9: 'VP9',
      mpeg2: 'MPEG-2',
    };
    return codec ? labels[codec] || codec.toUpperCase() : '';
  }

  onTitleClick(row: TorrentSearchResult): void {
    const url = row.infoUrl;
    if (url) {
      window.open(url, '_blank');
    }
  }

  onRowClick(row: TorrentSearchResult): void {
    const downloadUrl = row.magnetUrl || row.downloadUrl;
    if (!downloadUrl) {
      return;
    }
    const dialogRef = this.dialog.open(DownloadOptionComponent, {
      data: {
        downloadUrl: downloadUrl,
        workId: this.workId,
        mediaType: this.mediaType,
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
