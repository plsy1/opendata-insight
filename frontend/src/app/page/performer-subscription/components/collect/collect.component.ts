import { TranslateModule } from '@ngx-translate/core';
import { Component } from '@angular/core';
import { PerformerSubscriptionService } from '../../service/performer-subscription.service';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Actress } from '../../model/actor-information.interface';

@Component({
  selector: 'app-list-performer-collect',
  standalone: true,
  imports: [
    CommonModule,
    TranslateModule,
    MatIconModule,
    MatCardModule,
    MatButtonModule,
    MatMenuModule,
  ],
  templateUrl: './collect.component.html',
  styleUrl: './collect.component.css',
})
export class PerformerCollectionListComponent {
  ActressList: Actress[] = [];

  dragSourceIndex: number | null = null;
  dragOverIndex: number | null = null;

  // Touch drag state
  private touchSourceIndex: number | null = null;
  private touchClone: HTMLElement | null = null;
  private touchCurrentOverIndex: number | null = null;
  private touchStartX = 0;
  private touchStartY = 0;
  private hasTouchMoved = false;

  constructor(
    public PerformerSubscriptionService: PerformerSubscriptionService,
    private router: Router,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.loadActressCollect();
  }

  loadActressCollect(): void {
    this.PerformerSubscriptionService.getActressCollect().subscribe({
      next: (data: Actress[]) => {
        this.ActressList = data;
      },
      error: (error) => {
        console.error('Error fetching actress feeds:', error);
        this.snackBar.open('Failed to load actress collection', 'Close', {
          duration: 2000,
        });
      },
    });
  }

  /* ── Native Drag (Desktop) ────────── */

  onDragStart(event: DragEvent, index: number) {
    this.dragSourceIndex = index;
    event.dataTransfer!.effectAllowed = 'move';
    const el = event.target as HTMLElement;
    setTimeout(() => el.classList.add('dragging'), 0);
  }

  onDragOver(event: DragEvent, index: number) {
    event.preventDefault();
    event.dataTransfer!.dropEffect = 'move';
    if (index !== this.dragSourceIndex) {
      this.dragOverIndex = index;
    }
  }

  onDragLeave(index: number) {
    if (this.dragOverIndex === index) {
      this.dragOverIndex = null;
    }
  }

  onDragDrop(event: DragEvent, index: number) {
    event.preventDefault();
    this.swapCards(this.dragSourceIndex!, index);
    this.dragOverIndex = null;
  }

  onDragEnd() {
    this.dragSourceIndex = null;
    this.dragOverIndex = null;
  }

  /* ── Touch Drag (Mobile) ──────────── */

  onTouchStart(event: TouchEvent, index: number) {
    this.touchSourceIndex = index;
    this.hasTouchMoved = false;
    const touch = event.touches[0];
    this.touchStartX = touch.clientX;
    this.touchStartY = touch.clientY;
  }

  onTouchMove(event: TouchEvent) {
    if (this.touchSourceIndex === null) return;
    const touch = event.touches[0];
    const dx = touch.clientX - this.touchStartX;
    const dy = touch.clientY - this.touchStartY;

    if (!this.hasTouchMoved && Math.abs(dx) < 10 && Math.abs(dy) < 10) return;
    this.hasTouchMoved = true;
    event.preventDefault();

    if (!this.touchClone) {
      const card = (event.target as HTMLElement).closest('.actress-card') as HTMLElement;
      if (!card) return;
      this.touchClone = card.cloneNode(true) as HTMLElement;
      this.touchClone.classList.add('touch-drag-clone');
      this.touchClone.style.width = card.offsetWidth + 'px';
      this.touchClone.style.height = card.offsetHeight + 'px';
      document.body.appendChild(this.touchClone);
      card.classList.add('dragging');
    }
    this.touchClone.style.left = (touch.clientX - 40) + 'px';
    this.touchClone.style.top = (touch.clientY - 40) + 'px';

    this.touchClone.style.pointerEvents = 'none';
    const el = document.elementFromPoint(touch.clientX, touch.clientY);
    this.touchClone.style.pointerEvents = '';
    const overCard = el?.closest('.actress-card') as HTMLElement | null;

    document.querySelectorAll('.actress-card.drag-over').forEach(c => c.classList.remove('drag-over'));
    this.touchCurrentOverIndex = null;

    if (overCard) {
      const cards = Array.from(overCard.parentElement!.querySelectorAll('.actress-card'));
      const overIdx = cards.indexOf(overCard);
      if (overIdx >= 0 && overIdx !== this.touchSourceIndex) {
        overCard.classList.add('drag-over');
        this.touchCurrentOverIndex = overIdx;
      }
    }
  }

  onTouchEnd(event: TouchEvent) {
    if (this.hasTouchMoved && this.touchSourceIndex !== null && this.touchCurrentOverIndex !== null) {
      event.preventDefault();
      this.swapCards(this.touchSourceIndex, this.touchCurrentOverIndex);
    }

    if (this.touchClone) {
      this.touchClone.remove();
      this.touchClone = null;
    }
    document.querySelectorAll('.actress-card.dragging').forEach(c => c.classList.remove('dragging'));
    document.querySelectorAll('.actress-card.drag-over').forEach(c => c.classList.remove('drag-over'));
    this.touchSourceIndex = null;
    this.touchCurrentOverIndex = null;
    this.hasTouchMoved = false;
  }

  /* ── Swap Logic ───────────────────── */

  private swapCards(fromIndex: number, toIndex: number) {
    if (fromIndex === toIndex) return;
    const temp = this.ActressList[fromIndex];
    this.ActressList[fromIndex] = this.ActressList[toIndex];
    this.ActressList[toIndex] = temp;
    
    // Sync to backend
    this.PerformerSubscriptionService.updateActorOrder(
      'collect',
      this.ActressList.map(a => a.name)
    ).subscribe({
      error: (err) => {
        console.error('Failed to sync order to backend:', err);
        this.snackBar.open('Failed to save order', 'Close', { duration: 2000 });
      }
    });
  }

  /* ── Other ────────────────────────── */

  onUnsubscribeClick(event: MouseEvent, movie: any): void {
    event.stopPropagation();

    this.PerformerSubscriptionService.removeActressCollect(
      movie.name
    ).subscribe({
      next: () => {
        this.snackBar.open('Unsubscribed successfully', 'Close', {
          duration: 2000,
        });
        this.loadActressCollect();
      },
      error: (error) => {
        console.error('Failed to unsubscribe:', error);
        this.snackBar.open('Failed to unsubscribe', 'Close', {
          duration: 2000,
        });
      },
    });
  }

  async onClick(name: string) {
    try {
      this.router.navigate(['/performer', name]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  contextActress: any;

  openMenu(event: Event, actress: any) {
    event.stopPropagation();
    this.contextActress = actress;
  }
}
