import { CommonService } from '../../../common.service';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { MoviePoster } from '../../../models/movie-data.interface';
import { ActorProfile } from '../../performer-subscription/model/actor-information.interface';

@Injectable({
  providedIn: 'root',
})
export class PerformerService {
  constructor(private common: CommonService, private http: HttpClient) {}

  performerInformation: ActorProfile | null = null;
  productionInformation: MoviePoster[] | null = null;

  name: string = '';
  searchKeyWords: string = '';
  page: number = 1;
  actressNumberFilter: string = '0';

  savePerformerInformation(data: ActorProfile) {
    this.performerInformation = data;
  }

  saveProductionInformation(data: MoviePoster[]) {
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

  addActorCollect(name: string): Observable<void> {
    return this.common.request<void>('POST', 'feed/actorCollect', {
      params: { name },
    });
  }

  addActorSubscribe(name: string): Observable<void> {
    return this.common.request<void>('POST', 'feed/actorSubscribe', {
      params: { name },
    });
  }

  getActorInformation(name: string): Observable<ActorProfile> {
    return this.common.request<ActorProfile>('GET', 'avbase/actorInformation', {
      params: { name },
    });
  }

  getMoviesByActorName(name: string, page: number): Observable<MoviePoster[]> {
    return this.common.request<MoviePoster[]>('GET', 'avbase/moviesOfActor', {
      params: { name: name, page },
    });
  }

  isEnableBlur$(): Observable<boolean> {
    return this.common.enableBlur$;
  }

  get enableBlur(): boolean {
    return this.common.enableBlur;
  }
}
