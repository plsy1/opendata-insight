import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CommonService } from '../../../common.service';
import { KeywordFeed } from '../models/production-subscription.interface';

import { MovieData } from '../../../models/movie-data.interface';

@Injectable({
  providedIn: 'root',
})
export class ProductionSubscriptionService {
  constructor(private common: CommonService) {}

  getKeywordFeeds(): Observable<MovieData[]> {
    return this.common.request<MovieData[]>('GET', 'feed/movieSubscribe');
  }

  getDownloadedKeywordsFeedListGet(): Observable<KeywordFeed[]> {
    return this.common.request<KeywordFeed[]>('GET', 'feed/movieDownloaded');
  }
  isEnableBlur$(): Observable<boolean> {
    return this.common.enableBlur$;
  }

  get enableBlur(): boolean {
    return this.common.enableBlur;
  }
}
