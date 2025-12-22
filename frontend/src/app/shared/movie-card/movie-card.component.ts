import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTooltipModule } from '@angular/material/tooltip';
import { SharedServiceService } from '../shared-service.service';
import { Router } from '@angular/router';
import { MatMenuModule } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';
@Component({
  selector: 'app-movie-card',
  standalone: true,
  imports: [CommonModule, MatMenuModule, MatIconModule, MatTooltipModule],
  templateUrl: './movie-card.component.html',
  styleUrls: ['./movie-card.component.scss'],
})
export class MovieCardComponent {
  @Input() id!: string;
  @Input() title!: string;
  @Input() imgUrl!: string;
  @Input() releaseDate?: string;
  @Input() actors: string[] = [];
  @Input() rank?: string;
  @Input() hideImage = false;
  @Input() showID = true;
  @Input() showDetialButton = false;
  @Input() enableBlur: boolean | null = false;

  inLibrary: boolean = false;
  libraryLink?: string;
  imageLoaded = false;

  @Output() movieClick = new EventEmitter<string>();
  @Output() movieDelete = new EventEmitter<string>();

  constructor(
    private shareService: SharedServiceService,
    private router: Router
  ) {}

  onImageError(event: Event) {
    (event.target as HTMLImageElement).src = '';
  }

  onClick() {
    this.movieClick.emit(this.id || this.title);
  }

  get showImage(): boolean {
    return !this.hideImage;
  }

  get displayPrefix(): string | null {
    return this.rank ?? this.id ?? null;
  }

  onInLibraryClick(event: Event) {
    event.stopPropagation();
    if (this.libraryLink) {
      window.open(this.libraryLink, '_blank');
    } else {
      console.warn('libraryLink is empty');
    }
  }
  onImageLoad() {
    if (this.imageLoaded) return;
    this.imageLoaded = true;
    this.shareService
      .checkMovieExists(this.id + this.title)
      .subscribe((res) => {
        this.inLibrary = res.exists;
        if (this.inLibrary === true) {
          this.libraryLink = res.indexLink;
        }
      });
  }

  onActorClick(actor: string, event: MouseEvent) {
    event.stopPropagation();
    this.router.navigate(['/performer', actor]);
  }

  onUnsubscribeClick(event: MouseEvent): void {
    event.stopPropagation();

    this.shareService.removeKeywordsRSS(this.title).subscribe({
      next: () => {
        this.movieDelete.emit();
      },
      error: (error) => {
        console.error('Failed to remove RSS feed:', error);
      },
    });
  }
}
