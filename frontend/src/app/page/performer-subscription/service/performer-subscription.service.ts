import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CommonService } from '../../../common.service';

@Injectable({
  providedIn: 'root',
})
export class PerformerSubscriptionService {
  constructor(private common: CommonService) {}

  getActressCollect(): Observable<any> {
    return this.common.request<any>('GET', 'feed/actorCollect');
  }

  removeActressCollect(name: string): Observable<any> {
    return this.common.request<any>('DELETE', 'feed/actorCollect', {
      params: { name: name },
    });
  }

  getActressFeed(): Observable<any> {
    return this.common.request<any>('GET', 'feed/actorSubscribe');
  }

  removeFeedsRSS(urlParam: string): Observable<any> {
    return this.common.request<any>('DELETE', 'feed/actorSubscribe', {
      params: { name: urlParam },
    });
  }

  isEnableBlur$(): Observable<boolean> {
    return this.common.enableBlur$;
  }

  get enableBlur(): boolean {
    return this.common.enableBlur;
  }
}
