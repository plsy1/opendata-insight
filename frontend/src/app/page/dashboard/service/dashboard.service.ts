import { Injectable } from '@angular/core';
import { CommonService } from '../../../common.service';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  constructor(private common: CommonService) {}

  getEmbyItemTotalCount(): Observable<any> {
    return this.common.request<any>('GET', 'emby/get_item_counts');
  }

  getEmbyLatestItems(): Observable<any> {
    return this.common.request<any>('GET', 'emby/get_latest');
  }

  getEmbyResumeItems(): Observable<any> {
    return this.common.request<any>('GET', 'emby/get_resume');
  }

  getEmbyViews(): Observable<any> {
    return this.common.request<any>('GET', 'emby/get_views');
  }

  isEnableBlur$(): Observable<boolean> {
    return this.common.enableBlur$;
  }

  get enableBlur(): boolean {
    return this.common.enableBlur;
  }
}
