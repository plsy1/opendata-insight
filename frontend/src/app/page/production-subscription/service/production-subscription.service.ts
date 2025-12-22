import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CommonService } from '../../../common.service';
import { KeywordFeed } from '../models/production-subscription.interface';

@Injectable({
  providedIn: 'root',
})
export class ProductionSubscriptionService {
  constructor(private common: CommonService) {}

  getKeywordFeeds(): Observable<KeywordFeed[]> {
    return this.common.request<KeywordFeed[]>(
      'GET',
      'feed/getKeywordsFeedList'
    );
  }

  getDownloadedKeywordsFeedListGet(): Observable<KeywordFeed[]> {
    return this.common.request<KeywordFeed[]>(
      'GET',
      'feed/getDownloadedKeywordsFeedList'
    );
  }
      isEnableBlur$(): Observable<boolean> {
    return this.common.enableBlur$;
  }

  get enableBlur(): boolean {
    return this.common.enableBlur;
  }
}
