import { CommonService } from './../../../../common.service';
import { Component, OnInit, OnDestroy, Inject, PLATFORM_ID } from '@angular/core';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { RouterModule } from '@angular/router';
import { HomeService } from '../../service/home.service';
import { TranslateModule } from '@ngx-translate/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [MatSidenavModule, MatListModule, RouterModule, TranslateModule, CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css'],
})
export class SidebarComponent implements OnInit, OnDestroy {
  public version: string = '';

  constructor(
    public homeService: HomeService,
    private common: CommonService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    this.checkScreenSize();
    window.addEventListener('resize', this.checkScreenSize.bind(this));
    this.common.getSystemVersion().subscribe((res) => {
      if (res && res.version) {
        this.version = res.version;
      }
    });
  }

  ngOnDestroy(): void {
    window.removeEventListener('resize', this.checkScreenSize.bind(this));
  }

    checkScreenSize(): void {
    const screenWidth = window.innerWidth;
  this.homeService.isSidebarOpen = screenWidth >= 768;
  }

  logout(): void {
    this.common.logout()
  }
}