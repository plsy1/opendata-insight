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
import { MovieInformation } from './models/movie-information.interface';
import { createDefaultMovieInformation } from './utils/default-movie-info';

@Component({
  selector: 'app-production-information',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatIconModule,
  ],
  templateUrl: './production-information.component.html',
  styleUrl: './production-information.component.css',
})
export class ProductionInformationComponent implements OnInit {
  movieData: MovieInformation = createDefaultMovieInformation();
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

  loadMovieData(movieUrl: string): void {
    this.isLoading = true;

    this.ProductionInformationService.getSingleProductionInformation(
      encodeURIComponent(movieUrl)
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
        this.movieData?.props?.pageProps?.work?.casts
          ?.map((cast: any) => cast?.actor?.name)
          ?.filter((name: string) => !!name)
          ?.slice(0, 3)
          ?.join(',') || '';

      this.router.navigate(
        ['/torrents', this.movieData.props.pageProps.work.work_id],
        {
          queryParams: {
            fullId: this.movieId,
            Id: this.movieData.props.pageProps.work.work_id,
          },
        }
      );
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  subscribeToMovie(): void {
    const work = this.movieData.props.pageProps.work;
    const actorNames = work.casts
      .map((c: { actor: { name: string } }) => c.actor.name)
      .join(', ');
    this.ProductionInformationService.addProductionSubscribe(
      actorNames,
      this.movieData.props.pageProps.work.work_id,
      this.movieData.props.pageProps.work.products[0].image_url ?? '',
      this.movieId
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
}
