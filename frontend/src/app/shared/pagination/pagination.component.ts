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
  @Input() hasPrevious?: boolean;
  @Input() showPageInfo = true;

  get canGoPrevious(): boolean {
    return this.hasPrevious !== undefined ? this.hasPrevious : this.page > 1;
  }

  @Output() previousClick = new EventEmitter<void>();
  @Output() nextClick = new EventEmitter<void>();

  onPrevious() {
    this.previousClick.emit();
  }

  onNext() {
    this.nextClick.emit();
  }
}
