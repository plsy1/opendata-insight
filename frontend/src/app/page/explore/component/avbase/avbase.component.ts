import { Component, OnInit } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { MatTabsModule } from '@angular/material/tabs';
import { Router } from '@angular/router';
import { PageExploreServiceService } from '../../services/page-explore.service';
import { CommonModule } from '@angular/common';
import { AvbaseIndexData } from '../../models/page-explore';
import { MatIconModule } from '@angular/material/icon';
import { AvbaseEverydayReleaseByPrefix } from '../../models/avbase-everyday-release';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PaginationComponent } from '../../../../shared/pagination/pagination.component';
import { MovieCardComponent } from '../../../../shared/movie-card/movie-card.component';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatInputModule } from '@angular/material/input';

@Component({
  selector: 'app-avbase',
  standalone: true,
  imports: [
    MatTabsModule,
    MovieCardComponent,
    CommonModule,
    MatIconModule,
    MatTooltipModule,
    PaginationComponent,
    MatDatepickerModule,
    MatNativeDateModule,
    MatInputModule,
    TranslateModule,
  ],
  templateUrl: './avbase.component.html',
  styleUrl: './avbase.component.css',
})
export class AvbaseComponent implements OnInit {
  currentDate: Date = new Date();
  avbaseIndexData?: AvbaseIndexData;
  releaseData: AvbaseEverydayReleaseByPrefix[] = [];

  constructor(
    public PageExploreService: PageExploreServiceService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const cachedData = this.PageExploreService.getAvbaseIndexData();
    const cachedEveryReleaseData =
      this.PageExploreService.getAvbaseEverydayReleaseData();

    if (cachedData) {
      this.avbaseIndexData = cachedData;
    } else {
      this.loadAvbaseIndex();
    }

    if (cachedEveryReleaseData) {
      this.releaseData = cachedEveryReleaseData;
    } else {
      this.loadEverydayReleaseData();
    }
  }

  get yyyymmdd(): string {
    return (
      this.currentDate.getFullYear().toString() +
      String(this.currentDate.getMonth() + 1).padStart(2, '0') +
      String(this.currentDate.getDate()).padStart(2, '0')
    );
  }

  loadAvbaseIndex(): void {
    this.PageExploreService.getAvbaseIndex().subscribe({
      next: (data) => {
        this.avbaseIndexData = data;
        this.PageExploreService.setAvbaseIndexData(data);
      },
      error: (err) => {
        console.error('Failed to load Avbase index:', err);
      },
    });
  }

  loadEverydayReleaseData() {
    this.PageExploreService.getAvbaseReleaseByDate(this.yyyymmdd).subscribe({
      next: (data: AvbaseEverydayReleaseByPrefix[]) => {
        this.releaseData = data;
        this.PageExploreService.setAvbaseEverydayReleaseData(data);
      },
      error: (err) => console.error('Error fetching daily release:', err),
    });
  }

  async cardClick(name: string) {
    try {
      this.router.navigate(['/performer', name]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  async posterClick(work_id: string) {
    try {
      this.router.navigate(['/production', work_id]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  prevDay() {
    this.currentDate = new Date(this.currentDate);
    this.currentDate.setDate(this.currentDate.getDate() - 1);

    this.loadEverydayReleaseData();
  }

  nextDay() {
    this.currentDate = new Date(this.currentDate);
    this.currentDate.setDate(this.currentDate.getDate() + 1);

    this.loadEverydayReleaseData();
  }

  onDateChange(event: any) {
    if (event.value) {
      this.currentDate = new Date(event.value);
      this.loadEverydayReleaseData();
    }
  }
}
