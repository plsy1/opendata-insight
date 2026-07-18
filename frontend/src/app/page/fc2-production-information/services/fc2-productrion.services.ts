import { Injectable } from '@angular/core';
import { CommonService } from '../../../common.service';
import { Observable } from 'rxjs';
import { FC2ProductionInformation } from '../model/fc2-production.interface';

@Injectable({
  providedIn: 'root',
})
export class fc2ProductionService {
  constructor(private common: CommonService) {}

  getFC2ProductionInformation(number: string): Observable<FC2ProductionInformation> {
    return this.common.request<FC2ProductionInformation>('GET', 'fc2/details', {
      params: { number: number },
    });
  }
}
