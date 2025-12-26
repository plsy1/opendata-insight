import { Injectable } from '@angular/core';
import { CommonService } from '../../../common.service';
import { keywordsSearchResponse } from '../models/keywordSearch.interface';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
@Injectable({
  providedIn: 'root',
})
export class KeywordsSearchService {
  public discoverResults?: keywordsSearchResponse[];
  public searchKeyWords: string = '';
  public currentPage: number = 1;
  public discoverType: number = 1;
  public actressNumberFilter: string = '0';
  public selectedMovie: any = null;

  constructor(private common: CommonService, private http: HttpClient) {}

  saveState(
    results: keywordsSearchResponse[],
    keywords: string,
    page: number,
    actressNumberFilter: string
  ) {
    this.discoverResults = results;
    this.searchKeyWords = keywords;
    this.currentPage = page;
    this.actressNumberFilter = actressNumberFilter;
  }

  saveSelectedMovie(movie: any) {
    this.selectedMovie = movie;
  }

  getSelectedMovie() {
    return this.selectedMovie;
  }

  discoverByKeywords(filter_value: string, page: number): Observable<any> {
    return this.common.request<any>('GET', 'avbase/search', {
      params: {
        keywords: filter_value,
        page,
      },
    });
  }

    isEnableBlur$(): Observable<boolean> {
    return this.common.enableBlur$;
  }

  get enableBlur(): boolean {
    return this.common.enableBlur;
  }
}
