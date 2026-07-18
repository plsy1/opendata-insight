import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CommonService } from '../../../common.service';
import { Actress } from '../model/actor-information.interface';

@Injectable({
  providedIn: 'root',
})
export class PerformerSubscriptionService {
  constructor(private common: CommonService) {}

  getActressCollect(): Observable<Actress[]> {
    return this.common.request<Actress[]>('GET', 'feed/actorCollect');
  }

  removeActressCollect(name: string): Observable<void> {
    return this.common.request<void>('DELETE', 'feed/actorCollect', {
      params: { name: name },
    });
  }

  getActressFeed(): Observable<Actress[]> {
    return this.common.request<Actress[]>('GET', 'feed/actorSubscribe');
  }

  removeFeedsRSS(urlParam: string): Observable<void> {
    return this.common.request<void>('DELETE', 'feed/actorSubscribe', {
      params: { name: urlParam },
    });
  }

  isEnableBlur$(): Observable<boolean> {
    return this.common.enableBlur$;
  }

  get enableBlur(): boolean {
    return this.common.enableBlur;
  }

  updateActorOrder(type: 'subscribe' | 'collect', names: string[]): Observable<void> {
    return this.common.request<void>('PUT', 'feed/actorOrder', {
      body: {
        type: type,
        names: names,
      },
    });
  }
}
