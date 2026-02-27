import { TranslateModule } from '@ngx-translate/core';
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PerformerService } from '../../service/performer.service';
import { Router } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';

import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';
import { MatOptionModule } from '@angular/material/core';
import { MatSelectModule } from '@angular/material/select';

import { ActivatedRoute } from '@angular/router';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PaginationComponent } from '../../../../shared/pagination/pagination.component';

import { MovieCardComponent } from '../../../../shared/movie-card/movie-card.component';

@Component({
  selector: 'app-production-cards',
  standalone: true,
  templateUrl: './production-cards.component.html',
  styleUrls: ['./production-cards.component.css'],
  imports: [
    CommonModule,
    TranslateModule,
    MatProgressSpinnerModule,
    MatIconModule,
    MatFormFieldModule,
    FormsModule,
    MatOptionModule,
    MatSelectModule,
    MatTooltipModule,
    PaginationComponent,
    MovieCardComponent,
  ],
})
export class MovieCards implements OnInit {
  discoverResults: any[] = [];
  isLoading: boolean = false;
  searchKeyWords: string = '';
  page: number = 1;

  actressNumberFilter: string = '0';

  constructor(
    public service: PerformerService,
    private router: Router,
    private getRoute: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.getRoute.paramMap.subscribe((params) => {
      this.searchKeyWords = params.get('name') || '';
      if (this.searchKeyWords === this.service.searchKeyWords) {
        this.discoverResults = this.service.productionInformation;
        this.page = this.service.page;
        this.actressNumberFilter = this.service.actressNumberFilter;
      } else {
        this.service.saveSearchKeyWords(this.searchKeyWords);
        this.loadDiscoverData(this.searchKeyWords, this.page);
      }
    });
  }

  loadDiscoverData(name: string, page: number): void {
    if (this.isLoading) return;
    this.isLoading = true;
    this.discoverResults = [];
    this.service.getMoviesByActorName(name, page).subscribe({
      next: (data) => {
        this.discoverResults = data;
        this.isLoading = false;
        this.service.saveProductionInformation(data);
        this.service.savePage(this.page);
      },
      error: (error) => {
        console.error('Failed to load discover data:', error);
        this.isLoading = false;
      },
    });
  }

  onImageError(event: any): void {}

  async onMovieClick(movie: any) {
    try {
      this.router.navigate(['production', movie.full_id]);
    } catch (error) {}
  }

  loadPreviousPage(): void {
    if (this.page > 1) {
      this.page -= 1;
      this.loadDiscoverData(this.searchKeyWords, this.page);
    }
  }

  loadNextPage(): void {
    this.page += 1;
    this.loadDiscoverData(this.searchKeyWords, this.page);
  }
  shouldShowMovie(movie: any): boolean {
    if (!this.actressNumberFilter) return true;

    const actorCount = movie.actors?.length || 0;

    if (this.actressNumberFilter === '1') return actorCount === 1;
    if (this.actressNumberFilter === '2') return actorCount >= 2;

    return true;
  }

  onFilterChange(value: string) {
    this.service.saveActressNumberFilter(value);
  }
}
