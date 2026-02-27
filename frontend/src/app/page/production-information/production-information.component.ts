import { ProductionInformationService } from './service/production-information.service';
import { Component, OnInit, HostListener } from '@angular/core';
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

  // ── Lightbox ──────────────────────────
  lightboxIndex: number = -1;
  lbScale   = 1;
  lbTx      = 0;   // translateX in px
  lbTy      = 0;   // translateY in px
  lbDragging = false;
  private lbDragStart = { x: 0, y: 0, tx: 0, ty: 0 };

  get lightboxOpen(): boolean { return this.lightboxIndex >= 0; }
  /** Cover image prepended to sample images — used for both strip and lightbox */
  get allSampleImages(): string[] {
    const cover   = this.movieData?.products?.[0]?.image_url || '';
    const samples = (this.movieData?.products?.[0]?.sample_image_urls || []).map((s: any) => s['l'] || '');
    return cover ? [cover, ...samples] : samples;
  }
  get lightboxImages(): string[] { return this.allSampleImages; }
  get lightboxSrc(): string { return this.lightboxImages[this.lightboxIndex] || ''; }
  get lbTransform(): string {
    return `translate(${this.lbTx}px, ${this.lbTy}px) scale(${this.lbScale})`;
  }
  get lbCursor(): string {
    if (this.lbDragging) return 'grabbing';
    return this.lbScale > 1 ? 'grab' : 'default';
  }

  private resetLbTransform(): void { this.lbScale = 1; this.lbTx = 0; this.lbTy = 0; }

  openLightbox(index: number): void { this.lightboxIndex = index; this.resetLbTransform(); }
  closeLightbox(): void  { this.lightboxIndex = -1; this.resetLbTransform(); }
  prevImage(): void {
    this.resetLbTransform();
    this.lightboxIndex = (this.lightboxIndex - 1 + this.lightboxImages.length) % this.lightboxImages.length;
  }
  nextImage(): void {
    this.resetLbTransform();
    this.lightboxIndex = (this.lightboxIndex + 1) % this.lightboxImages.length;
  }

  /** Wheel-to-zoom centred on the cursor */
  onLbWheel(event: WheelEvent): void {
    event.preventDefault();
    event.stopPropagation();

    const img  = event.currentTarget as HTMLElement;
    const rect = img.getBoundingClientRect();

    // Mouse position relative to the image's current rendered top-left corner
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    // New scale clamped to [1, 5]
    const factor   = event.deltaY < 0 ? 1.12 : 1 / 1.12;
    const newScale = Math.min(5, Math.max(1, this.lbScale * factor));
    const ratio    = newScale / this.lbScale;

    // Correct zoom-to-cursor formula (derived from transform-origin:0 0):
    // newTx = tx + mouseX * (1 - ratio)
    // This keeps the screen-space position of (mouseX, mouseY) fixed as scale changes.
    this.lbTx    = this.lbTx + mouseX * (1 - ratio);
    this.lbTy    = this.lbTy + mouseY * (1 - ratio);
    this.lbScale = newScale;

    if (newScale === 1) { this.lbTx = 0; this.lbTy = 0; }
  }

  /** Pan by dragging when zoomed */
  onLbMouseDown(event: MouseEvent): void {
    if (this.lbScale <= 1) return;
    this.lbDragging = true;
    this.lbDragStart = { x: event.clientX, y: event.clientY, tx: this.lbTx, ty: this.lbTy };
    event.preventDefault();
  }

  @HostListener('document:mousemove', ['$event'])
  onLbMouseMove(event: MouseEvent): void {
    if (!this.lbDragging) return;
    this.lbTx = this.lbDragStart.tx + (event.clientX - this.lbDragStart.x);
    this.lbTy = this.lbDragStart.ty + (event.clientY - this.lbDragStart.y);
  }

  @HostListener('document:mouseup')
  onLbMouseUp(): void { this.lbDragging = false; }

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
