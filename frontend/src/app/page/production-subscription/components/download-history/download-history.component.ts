import { Component } from '@angular/core';
import { ProductionSubscriptionService } from '../../service/production-subscription.service';
import { CommonModule } from '@angular/common';
import { MovieData } from '../../../../models/movie-data.interface';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltip } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MovieCardComponent } from '../../../../shared/movie-card/movie-card.component';
@Component({
  selector: 'app-download-history',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatTooltip,
    MatMenuModule,
    MovieCardComponent,
  ],
  templateUrl: './download-history.component.html',
  styleUrl: './download-history.component.css',
})
export class DownloadHistoryComponent {
  keywordFeeds: MovieData[] = [];
  constructor(
    public ProductionSubscriptionService: ProductionSubscriptionService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.ProductionSubscriptionService.getDownloadedKeywordsFeedListGet().subscribe(
      {
        next: (data: MovieData[]) => {
          this.keywordFeeds = data;
        },
        error: (error) => {
          console.error('Error fetching keywords feed list', error);
        },
      }
    );
  }
  async posterClick(prefix: string, work_id: string) {
    try {
      this.router.navigate(['/production', prefix + ':' + work_id]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  onUnsubscribeClick(): void {
    this.ProductionSubscriptionService.getDownloadedKeywordsFeedListGet().subscribe(
      {
        next: (data: MovieData[]) => {
          this.keywordFeeds = data;
        },
        error: (error) => {
          console.error('Error fetching keywords feed list', error);
        },
      }
    );
  }
  getActorNames(movie: any): string[] {
    const actors = movie.actors || [];
    const casts = movie.casts || [];

    const names: string[] = [];
    const seen = new Set<string>();

    for (const a of [...actors, ...casts]) {
      const name = a?.name?.trim();
      if (name && !seen.has(name)) {
        seen.add(name);
        names.push(name);
      }
    }

    return names;
  }
}
