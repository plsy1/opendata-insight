import {
  Component,
  ElementRef,
  NgZone,
  OnDestroy,
  OnInit,
  ViewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltip } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { TranslateModule } from '@ngx-translate/core';

import { APP_PATHS } from '../../../../app-paths';
import { MovieFeedItem } from '../../../../models/movie-data.interface';
import { MovieCardComponent } from '../../../../shared/movie-card/movie-card.component';
import { ProductionSubscriptionService } from '../../service/production-subscription.service';

@Component({
  selector: 'app-download-history',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatTooltip,
    MatMenuModule,
    TranslateModule,
    MovieCardComponent,
  ],
  templateUrl: './download-history.component.html',
  styleUrl: './download-history.component.css',
})
export class DownloadHistoryComponent implements OnInit, OnDestroy {
  readonly pageSize = 30;
  keywordFeeds: MovieFeedItem[] = [];
  nextCursor: string | null = null;
  hasMore = true;
  isLoading = false;
  loadError = false;
  total = 0;

  private observer?: IntersectionObserver;

  @ViewChild('loadSentinel')
  set loadSentinel(element: ElementRef<HTMLElement> | undefined) {
    this.observer?.disconnect();
    if (!element) return;

    this.observer ??= new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          this.zone.run(() => this.loadNextPage());
        }
      },
      { rootMargin: '400px 0px' }
    );
    this.observer.observe(element.nativeElement);
  }

  constructor(
    public ProductionSubscriptionService: ProductionSubscriptionService,
    private router: Router,
    private zone: NgZone
  ) {}

  ngOnInit(): void {
    this.loadNextPage();
  }

  ngOnDestroy(): void {
    this.observer?.disconnect();
  }

  loadNextPage(): void {
    if (this.isLoading || !this.hasMore) return;

    this.isLoading = true;
    this.loadError = false;
    this.ProductionSubscriptionService.getDownloadedMoviePage(
      this.nextCursor,
      this.pageSize
    ).subscribe({
      next: (page) => {
        const knownIds = new Set(this.keywordFeeds.map((movie) => movie.id));
        this.keywordFeeds = [
          ...this.keywordFeeds,
          ...page.items.filter((movie) => !knownIds.has(movie.id)),
        ];
        this.nextCursor = page.next_cursor;
        this.hasMore = page.has_more;
        this.total = page.total;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error fetching download history', error);
        this.loadError = true;
        this.isLoading = false;
      },
    });
  }

  onMovieDelete(workId: string): void {
    this.keywordFeeds = this.keywordFeeds.filter((movie) => movie.id !== workId);
    this.total = Math.max(0, this.total - 1);
    if (this.hasMore) this.loadNextPage();
  }

  trackByMovie(_index: number, movie: MovieFeedItem): string {
    return movie.id;
  }

  posterClick(workId: string): void {
    this.router.navigate([APP_PATHS.movies, workId]);
  }
}
