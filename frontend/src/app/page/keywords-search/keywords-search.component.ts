import { keywordsSearchResponse } from './models/keywordSearch.interface';
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';
import { MatOptionModule } from '@angular/material/core';
import { MatSelectModule } from '@angular/material/select';
import { KeywordsSearchService } from './service/keywords-search.service';
import { ActivatedRoute } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { MatTooltipModule } from '@angular/material/tooltip';

import { PaginationComponent } from '../../shared/pagination/pagination.component';
import { MovieCardComponent } from '../../shared/movie-card/movie-card.component';

@Component({
  selector: 'app-keywords-search',
  standalone: true,
  imports: [
    CommonModule,
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

  templateUrl: './keywords-search.component.html',
  styleUrl: './keywords-search.component.css',
})
export class KeywordsSearchComponent implements OnInit {
  discoverResults?: keywordsSearchResponse[];
  isLoading: boolean = false;
  searchKeyWords: string = '';
  page: number = 1;

  actressNumberFilter: string = '0';

  libraryStatus: { [title: string]: boolean } = {};

  constructor(
    public keywordsService: KeywordsSearchService,
    private router: Router,
    private getRoute: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.getRoute.paramMap.subscribe((params) => {
      this.searchKeyWords = params.get('value') || '';
      if (
        this.keywordsService.searchKeyWords === this.searchKeyWords ||
        this.searchKeyWords === ''
      ) {
        this.discoverResults = this.keywordsService.discoverResults;
      } else {
        this.loadDiscoverData(this.searchKeyWords, this.page);
      }
    });
  }

  loadDiscoverData(filter_value: string, page: number): void {
    if (this.isLoading) return;
    this.isLoading = true;

    this.keywordsService
      .discoverByKeywords(filter_value, page)
      .pipe(
        catchError((error: HttpErrorResponse) => {
          console.error('Failed to load discover data:', error);
          this.isLoading = false;
          return throwError(() => error);
        })
      )
      .subscribe((data) => {
        this.discoverResults = data;
        this.isLoading = false;
        this.keywordsService.saveState(
          this.discoverResults!,
          this.searchKeyWords,
          this.page,
          this.actressNumberFilter
        );
      });
  }

  async onMovieClick(movie: any) {
    try {
      this.keywordsService.saveSelectedMovie(movie);
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
    this.keywordsService.actressNumberFilter = value;
  }
}
