import { TranslateModule } from '@ngx-translate/core';
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { ProductionSubscriptionListComponent } from './components/subscription/subscription.component';
import { DownloadHistoryComponent } from './components/download-history/download-history.component';
import { MatTabsModule } from '@angular/material/tabs';

@Component({
  selector: 'app-production-subscription',
  standalone: true,
  imports: [
    MatIconModule,
    CommonModule,
    TranslateModule,
    ProductionSubscriptionListComponent,
    DownloadHistoryComponent,
    MatTabsModule,
  ],
  templateUrl: './production-subscription.component.html',
  styleUrl: './production-subscription.component.css',
})
export class ProductionSubscriptionComponent {
  selectedTabIndex = 0;

  ngOnInit() {
    const savedIndex = sessionStorage.getItem('productionSubscriptionTabIndex');
    if (savedIndex !== null) {
      this.selectedTabIndex = +savedIndex;
    }
  }

  onTabChange(event: any) {
    sessionStorage.setItem('productionSubscriptionTabIndex', event.index);
  }
}
