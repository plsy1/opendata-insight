import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { Component, OnInit } from '@angular/core';
import { MatTabsModule } from '@angular/material/tabs';
import { AvbaseComponent } from './component/avbase/avbase.component';
import { FanzaComponent } from './component/fanza/fanza.component';
import { Fc2Component } from './component/fc2/fc2/fc2.component';

@Component({
  selector: 'app-explore',
  standalone: true,
  imports: [CommonModule, TranslateModule, AvbaseComponent, MatTabsModule, FanzaComponent, Fc2Component],
  templateUrl: './explore.component.html',
  styleUrls: ['./explore.component.css'],
})
export class ExploreComponent implements OnInit {
  selectedTabIndex = 0;

  ngOnInit() {
    const savedIndex = sessionStorage.getItem('exploreTabIndex');
    if (savedIndex !== null) {
      this.selectedTabIndex = +savedIndex;
    }
  }

  onTabChange(event: any) {
    sessionStorage.setItem('exploreTabIndex', event.index);
  }
}
