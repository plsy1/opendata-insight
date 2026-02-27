import { TranslateModule } from '@ngx-translate/core';
import { Component } from '@angular/core';
import { PerformerSubscriptionService } from '../../service/performer-subscription.service';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Actress } from '../../model/actor-information.interface';

@Component({
  selector: 'app-list-performer-collect',
  standalone: true,
  imports: [
    CommonModule,
    TranslateModule,
    MatIconModule,
    MatCardModule,
    MatButtonModule,
    MatMenuModule,
  ],
  templateUrl: './collect.component.html',
  styleUrl: './collect.component.css',
})
export class PerformerCollectionListComponent {
  ActressList: Actress[] = [];
  constructor(
    public PerformerSubscriptionService: PerformerSubscriptionService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadActressCollect();
  }

  loadActressCollect(): void {
    this.PerformerSubscriptionService.getActressCollect().subscribe({
      next: (data: Actress[]) => {
        this.ActressList = data;
      },
      error: (error) => {
        console.error('Error fetching actress feeds:', error);
        this.snackBar.open('Failed to load actress collection', 'Close', {
          duration: 2000,
        });
      },
    });
  }

  onUnsubscribeClick(event: MouseEvent, movie: any): void {
    event.stopPropagation();

    this.PerformerSubscriptionService.removeActressCollect(
      movie.name
    ).subscribe({
      next: () => {
        this.snackBar.open('Unsubscribed successfully', 'Close', {
          duration: 2000,
        });
        this.loadActressCollect();
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
