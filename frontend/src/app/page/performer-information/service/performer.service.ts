import { CommonService } from '../../../common.service';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class PerformerService {
  constructor(private common: CommonService, private http: HttpClient) {}

  performerInformation: any;
  productionInformation: any;

  name: string = '';
  searchKeyWords: string = '';
  page: number = 1;
  actressNumberFilter: string = '0';

  savePerformerInformation(data: any) {
    this.performerInformation = data;
  }

  saveProductionInformation(data: any) {
    this.productionInformation = data;
  }

  saveName(name: string) {
    this.name = name;
  }

  savePage(page: number) {
    this.page = page;
  }

  saveSearchKeyWords(searchKeyWords: string) {
    this.searchKeyWords = searchKeyWords;
  }

  saveActressNumberFilter(actressNumberFilter: string) {
    this.actressNumberFilter = actressNumberFilter;
  }

  addActorCollect(name: string): Observable<any> {
    return this.common.request<any>('POST', 'feed/actorCollect', {
      params: { name },
    });
  }

  addActorSubscribe(name: string): Observable<any> {
    return this.common.request<any>('POST', 'feed/actorSubscribe', {
      params: { name },
    });
  }

  getActorInformation(name: string): Observable<any> {
    return this.common.request<any>('GET', 'avbase/actorInformation', {
      params: { name },
    });
  }

  getMoviesByActorName(name: string, page: number): Observable<any> {
    return this.common.request<any>('GET', 'avbase/moviesOfActor', {
      params: { name: name, page },
    });
  }

  isEnableBlur$(): Observable<boolean> {
    return this.common.enableBlur$;
  }

  get enableBlur(): boolean {
    return this.common.enableBlur;
  }
}
