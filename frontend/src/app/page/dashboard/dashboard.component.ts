import { Component } from '@angular/core';
import { LibraryStatisticComponent } from './component/library-statistic/library-statistic.component';
import { LibraryViewComponent } from './component/library-view/library-view.component';
import { RecentlyAddedComponent } from './component/recently-added/recently-added.component';
import { ResumeWatchingComponent } from './component/resume-watching/resume-watching.component';
import { MatTabsModule } from '@angular/material/tabs';
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
export class DashboardComponent {}
