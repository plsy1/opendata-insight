import { Component, OnInit } from '@angular/core';
import { PageExploreServiceService } from '../../../services/page-explore.service';
import { fc2RankingItem, RankingType } from '../../../models/fc2.interface';
import { MovieCardComponent } from '../../../../../shared/movie-card/movie-card.component';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { PaginationComponent } from '../../../../../shared/pagination/pagination.component';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-fc2',
  standalone: true,
  imports: [
    MovieCardComponent,
    CommonModule,
    PaginationComponent,
    MatFormFieldModule,
    MatSelectModule,
    FormsModule,
  ],
  templateUrl: './fc2.component.html',
  styleUrl: './fc2.component.css',
})
export class Fc2Component implements OnInit {
  constructor(
    private router: Router,
    public PageExploreService: PageExploreServiceService
  ) {}

  RankingType = RankingType;

  rankingData: fc2RankingItem[] = [];

  currentPage: number = 1;
  currentRankingType = RankingType.Realtime;

  ngOnInit(): void {
    const cachedData = this.PageExploreService.getfc2RankingData();

    if (cachedData) {
      this.rankingData = cachedData;
      this.currentPage = this.PageExploreService.getfc2CurrentPage();
    } else {
      this.loadfc2RankingData(1);
    }
  }

  loadfc2RankingData(page: number): void {
    this.PageExploreService.getFC2Ranking(
      page,
      this.currentRankingType
    ).subscribe({
      next: (data) => {
        this.rankingData = data;
        this.PageExploreService.setfc2RankingData(data);
        this.PageExploreService.setfc2CurrentPage(page);
      },
      error: (error) => {
        console.error('Failed to fetch fc2 ranking:', error);
      },
    });
  }

  async posterClick(work_id: string) {
    try {
      this.router.navigate(['/production/fc2', work_id]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  prevPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadfc2RankingData(this.currentPage);
    }
  }

  nextPage(): void {
    if (this.currentPage < 5) {
      this.currentPage++;
      this.loadfc2RankingData(this.currentPage);
    }
  }

  rankingTypeLabels: Record<RankingType, string> = {
    [RankingType.Realtime]: 'Realtime',
    [RankingType.Daily]: 'Daily',
    [RankingType.Weekly]: 'Weekly',
    [RankingType.Monthly]: 'Monthly',
    [RankingType.Yearly]: 'Yearly',
  };

  onWorkRankingTypeChange(newType: RankingType) {
    this.currentRankingType = newType;
    this.loadfc2RankingData(1);
  }
}
