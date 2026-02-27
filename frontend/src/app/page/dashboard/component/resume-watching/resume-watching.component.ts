import { Component, OnInit } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { DashboardService } from './../../service/dashboard.service';
import { ResumeItem } from '../../models/dashboard.interface';
import { MoviePosterComponent } from '../../../../shared/movie-poster/movie-poster.component';
@Component({
  selector: 'app-resume-watching',
  standalone: true,
  imports: [CommonModule, MatCardModule,MoviePosterComponent, TranslateModule],
  templateUrl: './resume-watching.component.html',
  styleUrl: './resume-watching.component.css',
})
export class ResumeWatchingComponent implements OnInit {
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
}
