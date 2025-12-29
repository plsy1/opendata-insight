import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { EnvironmentConfig } from '../models/settings.interface';
import { CommonService } from '../../../common.service';
import { JobInfo } from '../models/job_info.interface';

@Injectable({
  providedIn: 'root',
})
export class SettingsService {
  constructor(private common: CommonService) {}

  updateEnvironment(env: EnvironmentConfig): Observable<boolean> {
    return this.common
      .request<{ success?: boolean }>('POST', 'system/update_environment', {
        body: env,
      })
      .pipe(map((data) => data.success ?? true));
  }

  getEnvironment(): Observable<EnvironmentConfig> {
    return this.common.request<EnvironmentConfig>(
      'GET',
      'system/get_environment'
    );
  }

  changePassword(
    username: string,
    old_password: string,
    new_password: string
  ): Observable<boolean> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('old_password', old_password);
    formData.append('new_password', new_password);

    return this.common
      .request<{ message: string }>('POST', 'auth/changepassword', {
        body: formData,
      })
      .pipe(map((data) => data.message === 'Password updated successfully'));
  }

  runBackgroundTask(job_id: string): Observable<{ message: string }> {
    return this.common.request<{ message: string }>(
      'POST',
      'background_task/run',
      {
        params: { job_id: job_id },
      }
    );
  }

  listBackgroundTasks(): Observable<JobInfo[]> {
    return this.common.request<JobInfo[]>('GET', 'background_task/list');
  }
}
