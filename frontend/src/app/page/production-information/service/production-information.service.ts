import { Injectable } from '@angular/core';
import { CommonService } from '../../../common.service';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ProductionInformationService {
  constructor(private common: CommonService) {}

  getSingleProductionInformation(work_id: string): Observable<any> {
    return this.common.request<any>('GET', 'avbase/movie/information', {
      params: { work_id: work_id },
    });
  }

  addProductionSubscribe(
    actors: string,
    keyword: string,
    img: string,
    link: string
  ): Observable<any> {
    return this.common.request<any>('POST', 'feed/addKeywords', {
      body: new URLSearchParams({ actors, keyword, img, link }).toString(),
      acceptJson: true,
    });
  }
}
