import { TranslateModule } from '@ngx-translate/core';
import { DownloadingTorrent } from './models/torrent.interface';
import { DownloadService } from './service/download.service';
import { switchMap } from 'rxjs/operators';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { interval, Subscription } from 'rxjs';
import { SpeedPipe } from '../../pipe/speed.pipe';
import { EtaPipe } from '../../pipe/eta.pipe';
import { FileSizePipe } from '../../pipe/file-size.pipe';
import { MatIcon } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-download',
  standalone: true,
  imports: [
    CommonModule,
    TranslateModule,
    MatCardModule,
    MatIcon,
    MatProgressBarModule,
    MatGridListModule,
    MatProgressSpinnerModule,
    SpeedPipe,
    EtaPipe,
    FileSizePipe,
    MatTooltipModule,
  ],
  templateUrl: './download.component.html',
  styleUrls: ['./download.component.css'],
})
export class DownloadComponent implements OnInit, OnDestroy {
  torrents: DownloadingTorrent[] = [];
  private refreshSub?: Subscription;

  constructor(private downloadService: DownloadService) {}

  ngOnInit() {
    this.downloadService.getDownloadingTorrents().subscribe({
      next: (data) => (this.torrents = data),
      error: (err) => console.error('Failed to load torrents', err),
    });

    this.refreshSub = interval(3000)
      .pipe(switchMap(() => this.downloadService.getDownloadingTorrents()))
      .subscribe({
        next: (data) => (this.torrents = data),
        error: (err) => console.error('Failed to load torrents', err),
      });
  }

  loadTorrents(): void {
    this.downloadService.getDownloadingTorrents().subscribe({
      next: (data) => (this.torrents = data),
      error: (err) => console.error(err),
    });
  }

  deleteTorrent(hash: string): void {
    this.downloadService.deleteTorrent(hash).subscribe({
      next: () => {
        this.loadTorrents();
      },
      error: (err) => console.error('Failed to delete torrent:', err),
    });
  }

  ngOnDestroy() {
    this.refreshSub?.unsubscribe();
  }
}
