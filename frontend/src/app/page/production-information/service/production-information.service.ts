import { Injectable } from '@angular/core';
import { CommonService } from '../../../common.service';
import { Observable } from 'rxjs';
import { MovieData } from '../models/movie-data.interface';

@Injectable({
  providedIn: 'root',
})
export class ProductionInformationService {
  constructor(private common: CommonService) {}

  getSingleProductionInformation(work_id: string): Observable<MovieData> {
    return this.common.request<MovieData>('GET', 'avbase/movieInformation', {
      params: { work_id: work_id },
    });
  }

  refreshSingleProductionInformation(work_id: string): Observable<MovieData> {
    return this.common.request<MovieData>(
      'POST',
      'avbase/movieInformation/refresh',
      { params: { work_id: work_id } }
    );
  }

  addProductionSubscribe(work_id: string): Observable<void> {
    return this.common.request<void>('POST', 'feed/movieSubscribe', {
      params: { work_id: work_id },
    });
  }
}
