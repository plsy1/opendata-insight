import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { DashboardService } from './../../service/dashboard.service';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';
import { EmbyLatestItem } from '../../models/dashboard.interface';
import { MoviePosterComponent } from '../../../../shared/movie-poster/movie-poster.component';
@Component({
  selector: 'app-recently-added',
  standalone: true,
  imports: [MatCardModule, MatButtonModule, CommonModule,MoviePosterComponent, TranslateModule],
  templateUrl: './recently-added.component.html',
  styleUrl: './recently-added.component.css',
})
export class RecentlyAddedComponent implements OnInit {
  @ViewChild('scrollContainer') scrollContainer!: ElementRef;
  latestItems: EmbyLatestItem[] = [];
  constructor(public dashboardService: DashboardService) {}
ngOnInit(): void {
  this.dashboardService.getEmbyLatestItems().subscribe({
    next: (data) => {
      this.latestItems = data;
    },
    error: (err) => {
      console.error('Failed to load Emby Recently Added data.', err);
    },
  });
}

onImageError(event: Event, item: any) {
  item.hideImage = true;
}

onItemClick() {
  
}

scrollLeft() {
  if (this.scrollContainer) {
    this.scrollContainer.nativeElement.scrollBy({ left: -600, behavior: 'smooth' });
  }
}

scrollRight() {
  if (this.scrollContainer) {
    this.scrollContainer.nativeElement.scrollBy({ left: 600, behavior: 'smooth' });
  }
}
}
