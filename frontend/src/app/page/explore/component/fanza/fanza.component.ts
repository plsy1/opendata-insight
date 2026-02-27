import { Component, OnInit } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { MatTabsModule } from '@angular/material/tabs';
import { Router } from '@angular/router';
import { PageExploreServiceService } from '../../services/page-explore.service';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { FormsModule } from '@angular/forms';
import { MatTooltipModule } from '@angular/material/tooltip';
import {
  RankingTypeOfWorks,
  ActressRanking,
  RankingItem,
} from '../../models/page-explore';

import { PaginationComponent } from '../../../../shared/pagination/pagination.component';
import { MovieCardComponent } from '../../../../shared/movie-card/movie-card.component';
@Component({
  selector: 'app-fanza',
  standalone: true,
  imports: [
    MatTabsModule,
    CommonModule,MovieCardComponent,
    MatIconModule,
    MatFormFieldModule,
    MatSelectModule,
    FormsModule,MatTooltipModule,PaginationComponent, TranslateModule
  ],
  templateUrl: './fanza.component.html',
  styleUrl: './fanza.component.css',
})
export class FanzaComponent implements OnInit {
  RankingTypeOfWorks = RankingTypeOfWorks;
  currentPage: number = 1;
  actressList: ActressRanking[] = [];
  workRankingType: RankingTypeOfWorks = RankingTypeOfWorks.Weekly;

  workList: RankingItem[] = [];
  currentWorkPage: number = 1;

  constructor(
    public PageExploreService: PageExploreServiceService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const cachedData = this.PageExploreService.getRankingData();

    if (cachedData && cachedData.length > 0) {
      this.actressList = cachedData;
      this.currentPage = this.PageExploreService.getLastPage();
      this.workRankingType = this.PageExploreService.getWorkRankingType();
    } else {
      this.PageExploreService.fetchActressRanking(1).subscribe({
        next: (data) => {
          this.actressList = data;
          this.currentPage = 1;
          this.PageExploreService.setRankingData(data, 1);
        },
        error: (error) => {
          console.error('Failed to fetch actress ranking:', error);
        },
      });
    }

    const cachedWorkData = this.PageExploreService.getWorkRankingData();
    if (cachedWorkData && cachedWorkData.length > 0) {
      this.workList = cachedWorkData;
      this.currentWorkPage = this.PageExploreService.getLastWorkPage();
    } else {
      this.PageExploreService.fetchWorkRanking(
        1,
        this.workRankingType
      ).subscribe({
        next: (data) => {
          this.workList = data;
          this.PageExploreService.setWorkRankingData(
            data,
            1,
            this.workRankingType
          );
          this.currentWorkPage = 1;
        },
        error: (error) => {
          console.error('Failed to fetch work ranking:', error);
        },
      });
    }
  }

  async cardClick(name: string) {
    try {
      this.router.navigate(['/performer', name]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  async posterClick(name: string) {
    try {
      this.router.navigate(['keywords', name]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  nextPage(): void {
    this.loadPage(this.currentPage + 1);
  }

  prevPage(): void {
    if (this.currentPage > 1) {
      this.loadPage(this.currentPage - 1);
    }
  }

  loadPage(page: number): void {
    this.PageExploreService.fetchActressRanking(page).subscribe({
      next: (data) => {
        this.actressList = data;
        this.currentPage = page;
        this.PageExploreService.setRankingData(data, page);
      },
      error: (err) => {
        console.error('Failed to fetch actress ranking:', err);
      },
    });
  }

  onWorkRankingTypeChange(value: RankingTypeOfWorks) {
    this.workRankingType = value;

    this.PageExploreService.fetchWorkRanking(1, this.workRankingType).subscribe(
      {
        next: (data) => {
          this.workList = data;
          this.PageExploreService.setWorkRankingData(
            data,
            1,
            this.workRankingType
          );
          this.currentWorkPage = 1;
        },
        error: (error) => {
          console.error('Failed to fetch work ranking:', error);
        },
      }
    );
  }

  nextWorkPage(): void {
    const nextPage = this.currentWorkPage + 1;
    this.PageExploreService.fetchWorkRanking(
      nextPage,
      this.workRankingType
    ).subscribe({
      next: (data) => {
        this.workList = data;
        this.currentWorkPage = nextPage;
        this.PageExploreService.setWorkRankingData(
          data,
          nextPage,
          this.workRankingType
        );
      },
      error: (error) => {
        console.error('Failed to fetch next work page:', error);
      },
    });
  }

  prevWorkPage(): void {
    if (this.currentWorkPage <= 1) return;
    const prevPage = this.currentWorkPage - 1;
    this.PageExploreService.fetchWorkRanking(
      prevPage,
      this.workRankingType
    ).subscribe({
      next: (data) => {
        this.workList = data;
        this.currentWorkPage = prevPage;
        this.PageExploreService.setWorkRankingData(
          data,
          prevPage,
          this.workRankingType
        );
      },
      error: (error) => {
        console.error('Failed to fetch previous work page:', error);
      },
    });
  }
}
