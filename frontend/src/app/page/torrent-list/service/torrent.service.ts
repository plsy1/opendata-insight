import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { CommonService } from '../../../common.service';

@Injectable({
  providedIn: 'root',
})
export class TorrentService {
  searchKeyWords: string = '';
  searchResults: any[] = [];

  constructor(private common: CommonService, private http: HttpClient) {}

  saveState(searchResults: any[], searchKeyWords: string) {
    this.searchKeyWords = searchKeyWords;
    this.searchResults = searchResults;
  }

  pushTorrent(
    keywords: string,
    movieId: string,
    downloadLink: string,
    savePath: string,
    performerName: string
  ): Observable<any> {
    return this.common.request<any>('POST', 'downloader/add_torrent_url', {
      params: {
        work_id: keywords,
        download_link: downloadLink,
        save_path: savePath
      },
      body: null,
    });
  }

  search(
    query: string,
    page: number = 1,
    pageSize: number = 10
  ): Observable<any> {
    return this.common.request<any>('GET', 'prowlarr/search', {
      params: {
        query,
        page,
        page_size: pageSize,
      },
    });
  }
}
