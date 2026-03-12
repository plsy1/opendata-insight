import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { DashboardService } from './../../service/dashboard.service';
import { ResumeItem } from '../../models/dashboard.interface';
import { MoviePosterComponent } from '../../../../shared/movie-poster/movie-poster.component';
@Component({
  selector: 'app-resume-watching',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MoviePosterComponent, TranslateModule],
  templateUrl: './resume-watching.component.html',
  styleUrl: './resume-watching.component.css',
})
export class ResumeWatchingComponent implements OnInit {
  @ViewChild('scrollContainer') scrollContainer!: ElementRef;
  resumeItems: ResumeItem[] = [];

  constructor(public dashboardService: DashboardService) {}

ngOnInit(): void {
  this.dashboardService.getEmbyResumeItems().subscribe({
    next: (data) => {
      this.resumeItems = data;
    },
    error: (err) => {
      console.error('Failed to load Emby Resume watching data.', err);
    },
  });
}

onImageError(event: Event, item: any) {
  item.hideImage = true;
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
