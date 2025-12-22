import { Component } from '@angular/core';
import { PerformerSubscriptionService } from '../../service/performer-subscription.service';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';

interface performerList {
  title: string;
  created_at: string;
  url: string;
  id: number;
  description: string;
}

@Component({
  selector: 'app-performer-subscription-list',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatCardModule,
    MatButtonModule,
    MatMenuModule,
  ],
  templateUrl: './subscription.component.html',
  styleUrl: './subscription.component.css',
})
export class PerformerSubscriptionListComponent {
  ActressList: performerList[] = [];
  constructor(
    public PerformerSubscriptionService: PerformerSubscriptionService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadActressFeed();
  }

  loadActressFeed(): void {
    this.PerformerSubscriptionService.getActressFeed().subscribe({
      next: (data: performerList[]) => {
        this.ActressList = data;
      },
      error: (error) => {
        console.error('Error fetching actress feeds:', error);
        this.snackBar.open('Failed to load feeds', 'Close', { duration: 2000 });
      },
    });
  }

  onUnsubscribeClick(event: MouseEvent, movie: any): void {
    event.stopPropagation();

    this.PerformerSubscriptionService.removeFeedsRSS(movie.title).subscribe({
      next: () => {
        this.snackBar.open('Unsubscribed successfully', 'Close', {
          duration: 2000,
        });
        this.loadActressFeed();
      },
      error: (error) => {
        console.error('Failed to unsubscribe:', error);
        this.snackBar.open('Failed to unsubscribe', 'Close', {
          duration: 2000,
        });
      },
    });
  }

  async onClick(name: string) {
    try {
      this.router.navigate(['/performer', name]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  contextActress: any;

  openMenu(event: Event, actress: any) {
    event.stopPropagation();
    this.contextActress = actress;
  }
}
