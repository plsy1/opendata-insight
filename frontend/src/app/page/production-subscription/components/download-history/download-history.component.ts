import { Component } from '@angular/core';
import { ProductionSubscriptionService } from '../../service/production-subscription.service';
import { CommonModule } from '@angular/common';
import { KeywordFeed } from '../../models/production-subscription.interface';
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
  keywordFeeds: KeywordFeed[] = [];
  constructor(
    public ProductionSubscriptionService: ProductionSubscriptionService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.ProductionSubscriptionService.getDownloadedKeywordsFeedListGet().subscribe(
      {
        next: (data: KeywordFeed[]) => {
          this.keywordFeeds = data;
        },
        error: (error) => {
          console.error('Error fetching keywords feed list', error);
        },
      }
    );
  }
  async onMovieCardClick(movie: KeywordFeed): Promise<void> {
    try {
      this.router.navigate(['production', movie.link]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  onUnsubscribeClick(): void {
    this.ProductionSubscriptionService.getDownloadedKeywordsFeedListGet().subscribe({
      next: (data: KeywordFeed[]) => {
        this.keywordFeeds = data;
      },
      error: (error) => {
        console.error('Error fetching keywords feed list', error);
      },
    });
  }
}
