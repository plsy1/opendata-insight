import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { LibraryStatisticComponent } from './component/library-statistic/library-statistic.component';
import { LibraryViewComponent } from './component/library-view/library-view.component';
import { RecentlyAddedComponent } from './component/recently-added/recently-added.component';
import { ResumeWatchingComponent } from './component/resume-watching/resume-watching.component';
import { MatTabChangeEvent, MatTabsModule } from '@angular/material/tabs';
import { DownloadStatisticComponent } from './component/download-statistic/download-statistic.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    LibraryStatisticComponent,
    LibraryViewComponent,
    RecentlyAddedComponent,
    ResumeWatchingComponent,
    MatTabsModule,
    DownloadStatisticComponent,
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent implements OnInit {
  selectedTabIndex = 0;

  constructor(
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.queryParamMap.subscribe((params) => {
      this.selectedTabIndex = params.get('tab') === 'statistics' ? 1 : 0;
    });
  }

  onTabChange(event: MatTabChangeEvent): void {
    const tab = event.index === 1 ? 'statistics' : null;
    if (this.route.snapshot.queryParamMap.get('tab') === tab) return;

    void this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { tab },
      queryParamsHandling: 'merge',
      replaceUrl: true,
    });
  }
}
