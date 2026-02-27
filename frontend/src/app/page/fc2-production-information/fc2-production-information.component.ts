import { TranslateModule } from '@ngx-translate/core';
import { Component, OnInit, HostListener } from '@angular/core';
import { fc2ProductionService } from './services/fc2-productrion.services';
import { FC2ProductionInformation } from './model/fc2-production.interface';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';

import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { MatIconModule } from '@angular/material/icon';

import { Router } from '@angular/router';

@Component({
  selector: 'app-fc2-production-information',
  standalone: true,
  imports: [
    CommonModule,
    TranslateModule,
    MatCardModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatIconModule,
  ],
  templateUrl: './fc2-production-information.component.html',
  styleUrl: './fc2-production-information.component.css',
})
export class Fc2ProductionInformationComponent implements OnInit {
  data: FC2ProductionInformation | null = null;
  work_id: string = '';
  isLoading: boolean = false;

  constructor(
    private fc2ProductionService: fc2ProductionService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  get allSampleImages(): string[] {
    if (!this.data) return [];
    return this.data.sample_images || [];
  }

  ngOnInit(): void {
    this.route.paramMap.subscribe((params) => {
      this.work_id = params.get('id') || '';
      this.loadProductionData();
    });
  }

  loadProductionData(): void {
    this.isLoading = true;
    this.fc2ProductionService
      .getFC2ProductionInformation(this.work_id)
      .subscribe({
        next: (data) => {
          this.data = data;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Failed to load fc2 data:', error);
          this.isLoading = false;
        },
      });
  }

  // ── Lightbox ──────────────────────────
  lightboxIndex: number = -1;
  lbScale   = 1;
  lbTx      = 0;   // translateX in px
  lbTy      = 0;   // translateY in px
  lbDragging = false;
  private lbDragStart = { x: 0, y: 0, tx: 0, ty: 0 };

  get lightboxOpen(): boolean { return this.lightboxIndex >= 0; }
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

    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    const factor   = event.deltaY < 0 ? 1.08 : 1 / 1.08;
    const newScale = Math.min(5, Math.max(1, this.lbScale * factor));
    const ratio    = newScale / this.lbScale;

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

  onWheelScroll(event: WheelEvent) {
    const container = event.currentTarget as HTMLElement;
    event.preventDefault();
    container.scrollLeft += event.deltaY;
  }

  async onSearchClick() {
    try {
      this.router.navigate(['/torrents', this.data?.article_id]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  async toSupjav() {
    try {
      window.open(`https://supjav.com/?s=${this.data?.article_id}`, '_blank');
    } catch (error) {
      console.error('Failed:', error);
    }
  }
  async toMissAV() {
    try {
      const lowerName = this.data?.product_id?.toLowerCase();
      window.open(`https://missav.ai/${lowerName}`, '_blank');
    } catch (error) {
      console.error('Failed:', error);
    }
  }
  async onSubscribeClick() {
    
  }
}
