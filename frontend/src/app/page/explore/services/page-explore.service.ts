import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AvbaseEverydayReleaseByPrefix } from '../models/avbase-everyday-release';
import { CommonService } from '../../../common.service';
import {
  RankingTypeOfWorks,
  ActressRanking,
  RankingItem,
  JavtrailersDailyRelease,
  AvbaseIndexData,
} from '../models/page-explore';

import { RankingType as fc2RankingType } from '../models/fc2.interface';
import { fc2RankingItem } from '../models/fc2.interface';

@Injectable({
  providedIn: 'root',
})
export class PageExploreServiceService {
  private actressRankingCache: ActressRanking[] = [];
  private lastFetchedPage: number = 1;
  private workRankingCache: RankingItem[] = [];
  private lastFetchedWorkPage: number = 1;
  private workRankingType: RankingTypeOfWorks = RankingTypeOfWorks.Weekly;
  private CalenderData: JavtrailersDailyRelease | null = null;
  private AvbaseIndexData: AvbaseIndexData | null = null;
  private avbaseEverydayReleaseData: AvbaseEverydayReleaseByPrefix[] | null =
    null;

  private fc2RankingData: fc2RankingItem[] | null = null;

  getJavtrailersData(): JavtrailersDailyRelease | null {
    return this.CalenderData;
  }
  setJavtrailersData(data: JavtrailersDailyRelease): void {
    this.CalenderData = data;
  }

  // ===== Avbase =====

  getAvbaseEverydayReleaseData(): AvbaseEverydayReleaseByPrefix[] | null {
    return this.avbaseEverydayReleaseData;
  }

  setAvbaseEverydayReleaseData(data: AvbaseEverydayReleaseByPrefix[]): void {
    this.avbaseEverydayReleaseData = data;
  }

  getAvbaseIndexData(): AvbaseIndexData | null {
    return this.AvbaseIndexData;
  }

  setAvbaseIndexData(data: AvbaseIndexData): void {
    this.AvbaseIndexData = data;
  }

  getfc2RankingData(): fc2RankingItem[] | null {
    return this.fc2RankingData;
  }

  setfc2RankingData(data: fc2RankingItem[]): void {
    this.fc2RankingData = data;
  }

  setRankingData(data: ActressRanking[], page: number): void {
    this.actressRankingCache = data;
    this.lastFetchedPage = page;
  }

  getRankingData(): ActressRanking[] {
    return this.actressRankingCache;
  }

  getLastPage(): number {
    return this.lastFetchedPage;
  }

  getWorkRankingType(): RankingTypeOfWorks {
    return this.workRankingType;
  }

  setWorkRankingData(
    data: RankingItem[],
    page: number,
    RankingType: RankingTypeOfWorks
  ): void {
    this.workRankingCache = data;
    this.lastFetchedWorkPage = page;
    this.workRankingType = RankingType;
  }

  getWorkRankingData(): RankingItem[] {
    return this.workRankingCache;
  }

  getLastWorkPage(): number {
    return this.lastFetchedWorkPage;
  }

  constructor(private http: HttpClient, private common: CommonService) {}

  fetchActressRanking(page: number): Observable<ActressRanking[]> {
    return this.common.request<ActressRanking[]>(
      'GET',
      'fanza/monthlyactress',
      {
        params: { page },
      }
    );
  }

  fetchWorkRanking(page: number, term: string): Observable<RankingItem[]> {
    return this.common.request<RankingItem[]>('GET', 'fanza/monthlyworks', {
      params: { page, term },
    });
  }

  getAvbaseIndex(): Observable<any> {
    return this.common.request<any>('GET', 'avbase/get_index');
  }

  getAvbaseReleaseByDate(yyyymmdd: string): Observable<any> {
    return this.common.request<any>('GET', 'avbase/get_release_by_date', {
      params: { yyyymmdd },
    });
  }

  getFC2Ranking(
    page: number,
    term: fc2RankingType
  ): Observable<fc2RankingItem[]> {
    return this.common.request<fc2RankingItem[]>('GET', 'fc2/ranking', {
      params: { page, term },
    });
  }

  getJavtrailersReleaseByDate(
    yyyymmdd: string
  ): Observable<JavtrailersDailyRelease> {
    return this.common.request<JavtrailersDailyRelease>(
      'GET',
      'javtrailers/getReleasebyDate',
      { params: { yyyymmdd } }
    );
  }

  isEnableBlur$(): Observable<boolean> {
    return this.common.enableBlur$;
  }

  get enableBlur(): boolean {
    return this.common.enableBlur;
  }
}
