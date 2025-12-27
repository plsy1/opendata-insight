import { ProductionSubscriptionService } from '../../service/production-subscription.service';
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { KeywordFeed } from '../../models/production-subscription.interface';
import { MatTooltip } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MovieCardComponent } from '../../../../shared/movie-card/movie-card.component';
import { MovieData } from '../../../../models/movie-data.interface';

@Component({
  selector: 'app-production-subscription-list',
  standalone: true,
  imports: [
    MatIconModule,
    CommonModule,
    MatMenuModule,
    MatTooltip,
    MovieCardComponent,
  ],
  templateUrl: './subscription.component.html',
  styleUrl: './subscription.component.css',
})
export class ProductionSubscriptionListComponent implements OnInit {
  keywordFeeds: MovieData[] = [];

  constructor(
    private router: Router,
    public ProductionSubscriptionService: ProductionSubscriptionService
  ) {}

  ngOnInit(): void {
    this.ProductionSubscriptionService.getKeywordFeeds().subscribe({
      next: (data: MovieData[]) => {
        this.keywordFeeds = data;
      },
      error: (error) => {
        console.error('Error fetching keywords feed list', error);
      },
    });
  }

  onUnsubscribeClick(): void {
    this.ProductionSubscriptionService.getKeywordFeeds().subscribe({
      next: (data: MovieData[]) => {
        this.keywordFeeds = data;
      },
      error: (error) => {
        console.error('Error fetching keywords feed list', error);
      },
    });
  }

  async posterClick(prefix: string, work_id: string) {
    try {
      this.router.navigate(['/production', prefix + ':' + work_id]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  getActorNames(actors: any[] = []): string[] {
    return actors.map((a) => a.name);
  }
}
