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

  discoverByActress(filter_value: string, page: number): Observable<any> {
    return this.common.request<any>('GET', 'avbase/actress/movies', {
      params: { name: filter_value, page },
    });
  }

  addActressCollect(url: string, title: string): Observable<any> {
    return this.common.request<any>('POST', 'feed/addActressCollect', {
      body: new URLSearchParams({ avatar_url: url, name: title }).toString(),
      acceptJson: true,
    });
  }

  addFeedsRSS(
    avatar_img_url: string,
    actor_name: string,
    description: string = ''
  ): Observable<any> {
    return this.common.request<any>('POST', 'feed/addFeeds', {
      body: new URLSearchParams({
        avatar_img_url,
        actor_name,
        description,
      }).toString(),
      acceptJson: true,
    });
  }

  getActressInformation(name: string): Observable<any> {
    return this.common.request<any>('GET', 'avbase/actress/information', {
      params: { name },
    });
  }

    isEnableBlur$(): Observable<boolean> {
    return this.common.enableBlur$;
  }

  get enableBlur(): boolean {
    return this.common.enableBlur;
  }
}
