import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CommonService } from '../../../common.service';
import { TorrentSearchResult } from '../models/torrent-search-result.interface';

export type DownloadMediaType = 'jav' | 'fc2';

@Injectable({
  providedIn: 'root',
})
export class TorrentService {
  searchKeyWords: string = '';
  searchResults: TorrentSearchResult[] = [];

  constructor(private common: CommonService) {}

  saveState(searchResults: TorrentSearchResult[], searchKeyWords: string): void {
    this.searchKeyWords = searchKeyWords;
    this.searchResults = searchResults;
  }

  pushTorrent(
    workId: string,
    downloadLink: string,
    savePath: string,
    mediaType?: DownloadMediaType
  ): Observable<void> {
    return this.common.request<void>('POST', 'downloader/add_torrent_url', {
      params: {
        work_id: workId,
        download_link: downloadLink,
        save_path: savePath,
        ...(mediaType ? { media_type: mediaType } : {}),
      },
      body: null,
    });
  }

  search(
    query: string,
    page: number = 1,
    pageSize: number = 10
  ): Observable<TorrentSearchResult[]> {
    return this.common.request<TorrentSearchResult[]>('GET', 'prowlarr/search', {
      params: {
        query,
        page,
        page_size: pageSize,
      },
    });
  }
}
