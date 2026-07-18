import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { combineLatest } from 'rxjs';

import { APP_PATHS } from '../../app-paths';
import { CommonService } from '../../common.service';
import { MovieCardComponent } from '../../shared/movie-card/movie-card.component';
import { PaginationComponent } from '../../shared/pagination/pagination.component';
import { FC2ProductionInformation } from '../fc2-production-information/model/fc2-production.interface';
import { fc2ProductionService } from '../fc2-production-information/services/fc2-productrion.services';
import { FC2SellerProfile } from './fc2-seller.interface';

@Component({
  selector: 'app-fc2-seller-information',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MovieCardComponent,
    PaginationComponent,
    TranslateModule,
  ],
  templateUrl: './fc2-seller-information.component.html',
  styleUrl: './fc2-seller-information.component.css',
})
export class Fc2SellerInformationComponent implements OnInit {
  sellerId = '';
  seller: FC2SellerProfile | null = null;
  works: FC2ProductionInformation[] = [];
  page = 1;
  total = 0;
  hasNext = false;
  isLoading = false;
  error = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private fc2Service: fc2ProductionService,
    public common: CommonService
  ) {}

  ngOnInit(): void {
    combineLatest([this.route.paramMap, this.route.queryParamMap]).subscribe(
      ([params, query]) => {
        const sellerId = params.get('sellerId') || '';
        const parsedPage = Number(query.get('page') || 1);
        this.sellerId = sellerId;
        this.page = Number.isFinite(parsedPage) && parsedPage > 0 ? parsedPage : 1;
        if (this.sellerId) this.loadSeller();
      }
    );
  }

  loadSeller(): void {
    this.isLoading = true;
    this.error = false;
    this.fc2Service.getFC2Seller(this.sellerId, this.page).subscribe({
      next: (response) => {
        this.seller = response.seller;
        this.works = response.works;
        this.total = response.total;
        this.hasNext = response.has_next;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Failed to load FC2 seller:', error);
        this.error = true;
        this.isLoading = false;
      },
    });
  }

  previousPage(): void {
    if (this.page <= 1) return;
    this.goToPage(this.page - 1);
  }

  nextPage(): void {
    if (!this.hasNext) return;
    this.goToPage(this.page + 1);
  }

  goToPage(page: number): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: page > 1 ? { page } : { page: null },
      queryParamsHandling: 'merge',
    });
  }

  openWork(articleId: string): void {
    this.router.navigate([APP_PATHS.fc2Movies, articleId]);
  }

  openSource(): void {
    if (!this.seller?.profile_url) return;
    window.open(this.seller.profile_url, '_blank', 'noopener');
  }

  workMeta(work: FC2ProductionInformation): string {
    return [work.duration, work.price].filter(Boolean).join(' · ');
  }
}
