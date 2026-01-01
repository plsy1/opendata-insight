// pagination.component.ts
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIcon } from '@angular/material/icon';

@Component({
  selector: 'app-pagination',
  standalone: true,
  imports: [CommonModule, MatProgressSpinnerModule,MatIcon],
  templateUrl: './pagination.component.html',
  styleUrl: './pagination.component.css',
})
export class PaginationComponent {
  @Input() page = 1;
  @Input() hasNext = true;

  @Output() previousClick = new EventEmitter<void>();
  @Output() nextClick = new EventEmitter<void>();

  onPrevious() {
    this.previousClick.emit();
  }

  onNext() {
    this.nextClick.emit();
  }
}
