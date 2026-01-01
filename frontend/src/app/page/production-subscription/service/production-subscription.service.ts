import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CommonService } from '../../../common.service';
import { MoviePoster } from '../../../models/movie-data.interface';

@Injectable({
  providedIn: 'root',
})
export class ProductionSubscriptionService {
  constructor(private common: CommonService) {}

  getKeywordFeeds(): Observable<MoviePoster[]> {
    return this.common.request<MoviePoster[]>('GET', 'feed/movieSubscribe');
  }

  getDownloadedKeywordsFeedListGet(): Observable<MoviePoster[]> {
    return this.common.request<MoviePoster[]>('GET', 'feed/movieDownloaded');
  }
  isEnableBlur$(): Observable<boolean> {
    return this.common.enableBlur$;
  }

  get enableBlur(): boolean {
    return this.common.enableBlur;
  }
}
