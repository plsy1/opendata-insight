import { ProductionSubscriptionService } from '../../service/production-subscription.service';
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltip } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MovieCardComponent } from '../../../../shared/movie-card/movie-card.component';
import { MovieFeedItem } from '../../../../models/movie-data.interface';
import { APP_PATHS } from '../../../../app-paths';
import { MatDialog } from '@angular/material/dialog';
import { SubscriptionRulesComponent } from '../../../settings/components/subscription-rules/subscription-rules.component';

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
  keywordFeeds: MovieFeedItem[] = [];

  constructor(
    private router: Router,
    private dialog: MatDialog,
    public ProductionSubscriptionService: ProductionSubscriptionService
  ) {}

  ngOnInit(): void {
    this.loadFeeds();
  }

  loadFeeds(): void {
    this.ProductionSubscriptionService.getKeywordFeeds().subscribe({
      next: (data) => {
        this.keywordFeeds = data;
      },
      error: (error) => {
        console.error('Error fetching keywords feed list', error);
      },
    });
  }

  onUnsubscribeClick(): void {
    this.loadFeeds();
  }

  editSubscriptionRules(movie: MovieFeedItem): void {
    this.dialog
      .open(SubscriptionRulesComponent, {
        data: { movie },
        width: 'min(920px, 94vw)',
        maxWidth: '94vw',
        maxHeight: '92vh',
        panelClass: 'subscription-rules-dialog',
      })
      .afterClosed()
      .subscribe((saved) => {
        if (saved) {
          this.loadFeeds();
        }
      });
  }

  async posterClick(work_id: string) {
    try {
      this.router.navigate([APP_PATHS.movies, work_id]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }
}
