import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-movie-poster',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './movie-poster.component.html',
  styleUrls: ['./movie-poster.component.scss'],
})
export class MoviePosterComponent {
  @Input() title: string = '';
  @Input() imgUrl: string | null = null;
  @Input() link: string | null = null;
  @Input() hideImage: boolean = false;
  @Input() enableBlur: boolean | null = false;

  onImageError(event: Event) {
    (event.target as HTMLImageElement).src = 'assets/logo.svg';
  }
}
