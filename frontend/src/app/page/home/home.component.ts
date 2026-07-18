import { SidebarComponent } from './component/sidebar/sidebar.component';
import { TopbarComponent } from './component/topbar/topbar.component';
import { DashboardComponent } from '../dashboard/dashboard.component';
import {
  RouterOutlet,
  Router,
  NavigationEnd,
  NavigationStart,
} from '@angular/router';
import {
  Component,
  ViewChild,
  ElementRef,
  AfterViewInit,
  OnDestroy,
} from '@angular/core';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    SidebarComponent,
    TopbarComponent,
    DashboardComponent,
    RouterOutlet,
  ],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent implements AfterViewInit, OnDestroy {
  @ViewChild('dashboard') dashboard!: ElementRef<HTMLElement>;

  private readonly scrollStorageKey = 'pageScrollPositions';
  private scrollPositions: Record<string, number> = {};
  private currentUrl = '';
  private isRestoring = false;
  private routerSubscription?: Subscription;
  private restoreTimers: ReturnType<typeof setTimeout>[] = [];
  private scrollListener?: () => void;

  constructor(private router: Router) {
    const saved = sessionStorage.getItem(this.scrollStorageKey);
    if (saved) {
      try {
        this.scrollPositions = JSON.parse(saved);
      } catch {
        sessionStorage.removeItem(this.scrollStorageKey);
      }
    }
  }

  ngAfterViewInit() {
    const el = this.dashboard.nativeElement;
    this.currentUrl = this.router.url;

    this.scrollListener = () => {
      if (!this.isRestoring) this.rememberScroll(this.currentUrl, el.scrollTop);
    };
    el.addEventListener('scroll', this.scrollListener, { passive: true });

    this.routerSubscription = this.router.events.subscribe((event) => {
      if (event instanceof NavigationStart) {
        this.rememberScroll(this.currentUrl, el.scrollTop);
      }
      if (event instanceof NavigationEnd) {
        this.currentUrl = event.urlAfterRedirects;
        this.restoreScroll(el, this.currentUrl);
      }
    });
    this.restoreScroll(el, this.currentUrl);
  }

  ngOnDestroy(): void {
    if (this.scrollListener) {
      this.dashboard.nativeElement.removeEventListener(
        'scroll',
        this.scrollListener
      );
    }
    this.routerSubscription?.unsubscribe();
    this.clearRestoreTimers();
  }

  private rememberScroll(url: string, scrollTop: number): void {
    if (!url) return;
    this.scrollPositions[url] = scrollTop;
    sessionStorage.setItem(
      this.scrollStorageKey,
      JSON.stringify(this.scrollPositions)
    );
  }

  private restoreScroll(el: HTMLElement, url: string): void {
    this.clearRestoreTimers();
    const target = this.scrollPositions[url] || 0;
    this.isRestoring = true;

    const delays = target > 0 ? [0, 50, 150, 350, 750, 1500] : [0];
    delays.forEach((delay, index) => {
      const timer = setTimeout(() => {
        if (this.currentUrl !== url) return;
        const maxScroll = Math.max(0, el.scrollHeight - el.clientHeight);
        el.scrollTo({ top: Math.min(target, maxScroll) });
        const isLast = index === delays.length - 1;
        if (target <= maxScroll || isLast) {
          this.isRestoring = false;
          this.clearRestoreTimers();
        }
      }, delay);
      this.restoreTimers.push(timer);
    });
  }

  private clearRestoreTimers(): void {
    this.restoreTimers.forEach((timer) => clearTimeout(timer));
    this.restoreTimers = [];
  }
}
