import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CommonService } from '../../../common.service';
import {
  MovieFeedItem,
  MovieFeedPage,
} from '../../../models/movie-data.interface';
import { MovieSubscriptionRules } from '../../../models/subscription-rules.interface';

@Injectable({
  providedIn: 'root',
})
export class ProductionSubscriptionService {
  constructor(private common: CommonService) {}

  getKeywordFeeds(): Observable<MovieFeedItem[]> {
    return this.common.request<MovieFeedItem[]>('GET', 'feed/movieSubscribe');
  }

  getDownloadedMoviePage(
    cursor: string | null = null,
    limit = 30
  ): Observable<MovieFeedPage> {
    return this.common.request<MovieFeedPage>('GET', 'feed/movieDownloaded', {
      params: { cursor, limit },
    });
  }

  updateMovieSubscriptionRules(
    workId: string,
    rules: MovieSubscriptionRules
  ): Observable<void> {
    return this.common.request<void>('PUT', 'feed/movieSubscribe/rules', {
      params: { work_id: workId },
      body: rules,
    });
  }
  isEnableBlur$(): Observable<boolean> {
    return this.common.enableBlur$;
  }

  get enableBlur(): boolean {
    return this.common.enableBlur;
  }
}
