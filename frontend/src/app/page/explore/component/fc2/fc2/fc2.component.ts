import { Component, OnInit } from '@angular/core';
import { PageExploreServiceService } from '../../../services/page-explore.service';
import { fc2RankingItem, RankingType } from '../../../models/fc2.interface';
import { MovieCardComponent } from '../../../../../shared/movie-card/movie-card.component';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-fc2',
  standalone: true,
  imports: [MovieCardComponent, CommonModule],
  templateUrl: './fc2.component.html',
  styleUrl: './fc2.component.css',
})
export class Fc2Component implements OnInit {
  constructor(
    private router: Router,
    public PageExploreService: PageExploreServiceService
  ) {}

  rankingData: fc2RankingItem[] = [];

  currentPage: number = 1;
  currentRankingType = RankingType.Realtime;

  ngOnInit(): void {
    const cachedData = this.PageExploreService.getfc2RankingData();

    if (cachedData) {
      this.rankingData = cachedData;
    } else {
      this.loadfc2RankingData();
    }
  }

  loadfc2RankingData(): void {
    this.PageExploreService.getFC2Ranking(
      this.currentPage,
      this.currentRankingType
    ).subscribe({
      next: (data) => {
        this.rankingData = data;
        this.PageExploreService.setfc2RankingData(data);
      },
      error: (error) => {
        console.error('Failed to fetch fc2 ranking:', error);
      },
    });
  }

  async posterClick(work_id: string) {
    try {
      this.router.navigate(['/torrents', work_id]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }
}
