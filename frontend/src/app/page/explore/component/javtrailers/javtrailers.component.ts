import { Component, OnInit } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { PageExploreServiceService } from '../../services/page-explore.service';
import { JavtrailersDailyRelease } from '../../models/page-explore';
import { MatCardModule } from '@angular/material/card';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

import { PaginationComponent } from '../../../../shared/pagination/pagination.component';
import { MovieCardComponent } from '../../../../shared/movie-card/movie-card.component';
@Component({
  selector: 'app-javtrailers',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatTooltipModule,
    PaginationComponent,MovieCardComponent, TranslateModule
  ],
  templateUrl: './javtrailers.component.html',
  styleUrls: ['./javtrailers.component.css'],
})
export class JavtrailersComponent implements OnInit {
  releaseData: JavtrailersDailyRelease | null = null;
  currentDate: Date = new Date();

  constructor(
    private router: Router,
    private pageExploreService: PageExploreServiceService
  ) {}

  ngOnInit(): void {
    const cachedData = this.pageExploreService.getJavtrailersData();

    if (cachedData) {
      this.releaseData = cachedData;
    } else {
      this.fetchReleaseData();
    }
  }

  get yyyymmdd(): string {
    return (
      this.currentDate.getFullYear().toString() +
      String(this.currentDate.getMonth() + 1).padStart(2, '0') +
      String(this.currentDate.getDate()).padStart(2, '0')
    );
  }

  fetchReleaseData() {
    this.pageExploreService
      .getJavtrailersReleaseByDate(this.yyyymmdd)
      .subscribe({
        next: (data) => {
          this.releaseData = data;
          this.pageExploreService.setJavtrailersData(data);
        },
        error: (err) => {
          console.error('Error fetching daily release:', err);
        },
        complete: () => {},
      });
  }

  posterClick(contentId: string) {
    this.router.navigate(['keywords', contentId]);
  }

  prevDay() {
    this.currentDate = new Date(this.currentDate);
    this.currentDate.setDate(this.currentDate.getDate() - 1);

    this.fetchReleaseData();
  }

  nextDay() {
    this.currentDate = new Date(this.currentDate);
    this.currentDate.setDate(this.currentDate.getDate() + 1);

    this.fetchReleaseData();
  }
}
