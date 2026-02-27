import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { catchError, map, throwError, Observable } from 'rxjs';
import { of, BehaviorSubject } from 'rxjs';
@Injectable({
  providedIn: 'root',
})
export class CommonService {
  apiUrl = '/api/v1';
  public isJumpFromProductionPage: boolean = false;
  public currentPerformer: string = '';

  private readonly BLUR_KEY = 'enableBlur';

  private enableBlurSubject = new BehaviorSubject<boolean>(this.loadBlur());
  enableBlur$ = this.enableBlurSubject.asObservable();

  get enableBlur(): boolean {
    return this.enableBlurSubject.value;
  }

  setEnableBlur(value: boolean) {
    this.enableBlurSubject.next(value);
    localStorage.setItem(this.BLUR_KEY, String(value));
  }

  private loadBlur(): boolean {
    const saved = localStorage.getItem(this.BLUR_KEY);
    return saved !== 'false';
  }

  toggleBlur(): void {
    const newValue = !this.enableBlur;
    this.setEnableBlur(newValue);
  }

  constructor(private router: Router, private http: HttpClient) {}

  logout(): void {
    localStorage.removeItem('loggedIn');
    localStorage.removeItem('access_token');
    this.router.navigate(['/login']);
  }

  request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    endpoint: string,
    {
      params,
      body,
      acceptJson = true,
    }: {
      params?: Record<string, any>;
      body?: any;
      acceptJson?: boolean;
    } = {}
  ): Observable<T> {
    const url = `${this.apiUrl}/${endpoint}`;

    const isStringBody = typeof body === 'string';
    const isFormData = body instanceof FormData;
    const isJsonBody = !isStringBody && !isFormData;

    const headersConfig: Record<string, string> = {
      Accept: acceptJson ? 'application/json' : '*/*',
      Authorization: `Bearer ${localStorage.getItem('access_token') ?? ''}`,
    };

    if (isStringBody) {
      headersConfig['Content-Type'] = 'application/x-www-form-urlencoded';
    } else if (isJsonBody) {
      headersConfig['Content-Type'] = 'application/json';
    }

    const headers = new HttpHeaders(headersConfig);

    let httpParams = new HttpParams();
    if (params) {
      for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null) {
          httpParams = httpParams.set(key, String(value));
        }
      }
    }

    const handleError = (error: HttpErrorResponse) => {
      if (error.status === 401) {
        this.logout();
      }
      console.error(`Request failed [${method}] ${endpoint}`, error);
      return throwError(() => new Error('Request failed'));
    };

    switch (method) {
      case 'POST':
        return this.http
          .post<T>(url, body ?? {}, { headers, params: httpParams })
          .pipe(catchError(handleError));
      case 'PUT':
        return this.http
          .put<T>(url, body ?? {}, { headers, params: httpParams })
          .pipe(catchError(handleError));
      case 'DELETE':
        return this.http
          .delete<T>(url, { headers, params: httpParams, body })
          .pipe(catchError(handleError));
      default:
        return this.http
          .get<T>(url, { headers, params: httpParams })
          .pipe(catchError(handleError));
    }
  }

  login(username: string, password: string): Observable<boolean> {
    const body = new URLSearchParams();
    body.set('username', username);
    body.set('password', password);

    return this.request<{ access_token?: string }>('POST', 'auth/login', {
      body: body.toString(),
      acceptJson: true,
    }).pipe(
      map((data) => {
        if (data.access_token) {
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('loggedIn', 'true');
          return true;
        }
        return false;
      }),
      catchError((error) => {
        console.error('Login request failed', error);
        return throwError(() => new Error('Request Failed'));
      })
    );
  }

  verifyTokenExpiration(): Observable<boolean> {
    const accessToken = localStorage.getItem('access_token') ?? '';

    const formData = new FormData();
    formData.append('access_token', accessToken);

    return this.request<boolean>('POST', 'auth/verify', {
      body: formData,
    }).pipe(
      catchError((error) => {
        console.error('Token verification failed', error);
        return of(false);
      })
    );
  }

  getSystemVersion(): Observable<{ version: string }> {
    return this.request<{ version: string }>('GET', 'system/version');
  }
}
