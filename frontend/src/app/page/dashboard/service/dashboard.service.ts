import { Injectable } from '@angular/core';
import { CommonService } from '../../../common.service';
import { Observable } from 'rxjs';
import {
  EmbyItemCounts,
  EmbyLatestItem,
  EmbyView,
  ResumeItem,
} from '../models/dashboard.interface';
import { StatAllResponse } from '../models/statistic.interface';

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  constructor(private common: CommonService) {}

  getEmbyItemTotalCount(): Observable<EmbyItemCounts> {
    return this.common.request<EmbyItemCounts>('GET', 'emby/get_item_counts');
  }

  getEmbyLatestItems(): Observable<EmbyLatestItem[]> {
    return this.common.request<EmbyLatestItem[]>('GET', 'emby/get_latest');
  }

  getEmbyResumeItems(): Observable<ResumeItem[]> {
    return this.common.request<ResumeItem[]>('GET', 'emby/get_resume');
  }

  getEmbyViews(): Observable<EmbyView[]> {
    return this.common.request<EmbyView[]>('GET', 'emby/get_views');
  }

  getAllStatistic(): Observable<StatAllResponse> {
    return this.common.request<StatAllResponse>('GET', 'statistic/all');
  }

  isEnableBlur$(): Observable<boolean> {
    return this.common.enableBlur$;
  }

  get enableBlur(): boolean {
    return this.common.enableBlur;
  }
}
