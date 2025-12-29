import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CommonService } from '../common.service';
import { HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class SharedServiceService {
  constructor(private common: CommonService, private http: HttpClient) {}

  checkMovieExists(title: string): Observable<any> {
    const url = `${this.common.apiUrl}/emby/exists?title=${encodeURIComponent(
      title
    )}`;
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('access_token') ?? ''}`,
    });

    return this.http.get<boolean>(url, { headers }).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          this.common.logout();
        }
        console.error('Request Failed', error);
        return throwError(() => new Error('Request Failed'));
      })
    );
  }

  removeMovieSubscribe(work_id: string): Observable<any> {
    return this.common.request<any>('DELETE', 'feed/movieSubscribe', {
      params: { work_id: work_id },
    });
  }
}
