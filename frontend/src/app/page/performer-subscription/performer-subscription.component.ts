import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { Component } from '@angular/core';
import { PerformerSubscriptionListComponent } from "./components/subscription/subscription.component";
import { PerformerCollectionListComponent } from './components/collect/collect.component';
import { MatTabsModule } from '@angular/material/tabs';
@Component({
  selector: 'app-performer-subscription',
  standalone: true,
  imports: [CommonModule, TranslateModule, PerformerSubscriptionListComponent, PerformerCollectionListComponent, MatTabsModule],
  templateUrl: './performer-subscription.component.html',
  styleUrl: './performer-subscription.component.css'
})
export class PerformerSubscriptionComponent {
    selectedTabIndex = 0;

  ngOnInit() {
    const savedIndex = sessionStorage.getItem('performerSubscriptionTabIndex');
    if (savedIndex !== null) {
      this.selectedTabIndex = +savedIndex;
    }
  }

  onTabChange(event: any) {
    sessionStorage.setItem('performerSubscriptionTabIndex', event.index);
  }

}
