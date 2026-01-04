import { ProductionInformationService } from './service/production-information.service';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatIconModule } from '@angular/material/icon';
import { CommonService } from '../../common.service';
import { MovieData } from './models/movie-data.interface';
import { createDefaultMovieInformation } from './utils/default-movie-info';
import { MatDivider } from '@angular/material/divider';

@Component({
  selector: 'app-production-information',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatIconModule,MatDivider
  ],
  templateUrl: './production-information.component.html',
  styleUrl: './production-information.component.css',
})
export class ProductionInformationComponent implements OnInit {
  movieData: MovieData = createDefaultMovieInformation();
  movieId: string = '';
  isLoading: boolean = false;

  constructor(
    private getRoute: ActivatedRoute,
    private ProductionInformationService: ProductionInformationService,
    private router: Router,
    private snackBar: MatSnackBar,
    private common: CommonService
  ) {}

  ngOnInit(): void {
    this.getRoute.paramMap.subscribe((params) => {
      this.movieId = params.get('id') || '';
      this.loadMovieData(this.movieId);
    });
  }

  loadMovieData(work_id: string): void {
    this.isLoading = true;

    this.ProductionInformationService.getSingleProductionInformation(
      encodeURIComponent(work_id)
    ).subscribe({
      next: (data) => {
        this.movieData = data;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Failed to load movie data:', error);
        this.isLoading = false;
      },
    });
  }

  async downloadMovie(): Promise<void> {
    try {
      this.common.isJumpFromProductionPage = true;
      this.common.currentPerformer =
        this.movieData.casts
          ?.map((cast: any) => cast?.name)
          ?.filter((name: string) => !!name)
          ?.slice(0, 3)
          ?.join(',') || '';
      this.router.navigate(['/torrents', this.movieData.work_id], {
        queryParams: {
          fullId: this.movieId,
          Id: this.movieData.work_id,
        },
      });
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  subscribeToMovie(): void {
    this.ProductionInformationService.addProductionSubscribe(
      this.movieData.work_id
    ).subscribe({
      next: (results) => {
        this.snackBar.open('Added successfully.', 'Close', { duration: 2000 });
      },
      error: (error) => {
        console.error('Failed:', error);
        this.snackBar.open('Failed to add subscription.', 'Close', {
          duration: 2000,
        });
      },
    });
  }

  async searchByActressName(name: string) {
    try {
      this.router.navigate(['/performer', name]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  onWheelScroll(event: WheelEvent) {
    const container = event.currentTarget as HTMLElement;
    event.preventDefault();
    container.scrollLeft += event.deltaY;
  }

  async toJable(name: string) {
    try {
      const lowerName = name.toLowerCase();
      window.open(`https://jable.tv/videos/${lowerName}/`, '_blank');
    } catch (error) {
      console.error('Failed:', error);
    }
  }
  async toMissAV(name: string) {
    try {
      const lowerName = name.toLowerCase();
      window.open(`https://missav.ai/${lowerName}`, '_blank');
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  get actors() {
    const casts = this.movieData?.casts;
    const actors = this.movieData?.actors;

    if (Array.isArray(casts) && casts.length > 0) {
      return casts;
    }

    if (Array.isArray(actors) && actors.length > 0) {
      return actors;
    }

    return [];
  }
}
