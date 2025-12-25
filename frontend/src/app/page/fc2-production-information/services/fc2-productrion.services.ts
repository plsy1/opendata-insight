import { Injectable } from '@angular/core';
import { CommonService } from '../../../common.service';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class fc2ProductionService {
  constructor(private common: CommonService) {}

  getFC2ProductionInformation(number: string): Observable<any> {
    return this.common.request<any>('GET', 'fc2/details', {
      params: { number: number },
    });
  }
}
