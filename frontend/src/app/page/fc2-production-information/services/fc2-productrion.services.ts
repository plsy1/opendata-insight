import { Injectable } from '@angular/core';
import { CommonService } from '../../../common.service';
import { Observable } from 'rxjs';
import { FC2ProductionInformation } from '../model/fc2-production.interface';
import { FC2SellerWorksResponse } from '../../fc2-seller-information/fc2-seller.interface';

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

  getFC2Seller(
    sellerId: string,
    page: number
  ): Observable<FC2SellerWorksResponse> {
    return this.common.request<FC2SellerWorksResponse>(
      'GET',
      `fc2/sellers/${encodeURIComponent(sellerId)}`,
      { params: { page } }
    );
  }
}
