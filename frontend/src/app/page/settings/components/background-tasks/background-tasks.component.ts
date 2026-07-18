import { Component, OnInit } from '@angular/core';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { SettingsService } from '../../service/settings.service';
import { JobInfo } from '../../models/job_info.interface';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar } from '@angular/material/snack-bar';
import { finalize } from 'rxjs';

@Component({
  selector: 'app-background-tasks',
  standalone: true,
  imports: [
    CommonModule,
    TranslateModule,
    MatCardModule,
    MatButtonModule,
  ],
  templateUrl: './background-tasks.component.html',
  styleUrl: './background-tasks.component.css',
})
export class BackgroundTasksComponent implements OnInit {
  jobs: JobInfo[] = [];
  isLoading = false;
  loadFailed = false;
  private readonly runningJobIds = new Set<string>();

  private readonly legacyJobIds: Record<string, string> = {
    'update emby': 'sync_emby_library',
    'clean image cache': 'clean_image_cache',
    'refresh subscribe': 'refresh_subscriptions',
    'update avbase release everyday': 'sync_avbase_releases',
    update_avbase_index_actor_service: 'sync_avbase_performers',
    'update fc2 ranking': 'sync_fc2_rankings',
    'update actor data periodic': 'refresh_performer_profiles',
  };

  constructor(
    private settingsService: SettingsService,
    private snackBar: MatSnackBar,
    private translate: TranslateService
  ) {}

  ngOnInit(): void {
    this.loadJobs();
  }

  run(jobId: string): void {
    if (this.runningJobIds.has(jobId)) {
      return;
    }

    this.runningJobIds.add(jobId);
    this.settingsService
      .runBackgroundTask(jobId)
      .pipe(finalize(() => this.runningJobIds.delete(jobId)))
      .subscribe({
        next: () => {
          this.snackBar.open(
            this.translate.instant('SETTINGS.TASK_QUEUED'),
            this.translate.instant('COMMON.CLOSE'),
            { duration: 2000, panelClass: ['success-snackbar'] }
          );
          this.loadJobs();
        },
        error: (err) => {
          console.error('Run failed:', err);
          this.snackBar.open(
            this.translate.instant('SETTINGS.TASK_RUN_FAILED'),
            this.translate.instant('COMMON.CLOSE'),
            { duration: 3000, panelClass: ['error-snackbar'] }
          );
        },
      });
  }

  loadJobs(): void {
    this.isLoading = true;
    this.loadFailed = false;
    this.settingsService.listBackgroundTasks().subscribe({
      next: (jobs) => {
        this.jobs = jobs;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Load jobs failed:', err);
        this.loadFailed = true;
        this.isLoading = false;
      },
    });
  }

  trackByJobId(_index: number, job: JobInfo): string {
    return job.id;
  }

  isRunning(jobId: string): boolean {
    return this.runningJobIds.has(jobId);
  }

  taskName(job: JobInfo): string {
    return this.taskTranslation(job, 'NAME') || job.name;
  }

  taskDescription(job: JobInfo): string {
    return this.taskTranslation(job, 'DESCRIPTION');
  }

  taskIcon(job: JobInfo): string {
    const icons: Record<string, string> = {
      sync_emby_library: 'fas fa-photo-film',
      clean_image_cache: 'fas fa-broom',
      refresh_subscriptions: 'fas fa-rss',
      sync_avbase_releases: 'fas fa-calendar-days',
      sync_avbase_performers: 'fas fa-users',
      sync_fc2_rankings: 'fas fa-ranking-star',
      refresh_performer_profiles: 'fas fa-address-card',
    };
    return icons[this.resolveTaskId(job)] || 'fas fa-gear';
  }

  taskTone(job: JobInfo): string {
    const tones: Record<string, string> = {
      sync_emby_library: 'tone-blue',
      clean_image_cache: 'tone-cyan',
      refresh_subscriptions: 'tone-violet',
      sync_avbase_releases: 'tone-amber',
      sync_avbase_performers: 'tone-pink',
      sync_fc2_rankings: 'tone-orange',
      refresh_performer_profiles: 'tone-green',
    };
    return tones[this.resolveTaskId(job)] || 'tone-blue';
  }

  formatInterval(job: JobInfo): string {
    const seconds = job.interval_seconds ?? this.parseLegacyInterval(job.trigger);
    if (!seconds) {
      return job.trigger || this.translate.instant('SETTINGS.TASK_UNKNOWN_SCHEDULE');
    }

    if (seconds % 86400 === 0) {
      const count = seconds / 86400;
      const key = count === 1 ? 'TASK_EVERY_DAY' : 'TASK_EVERY_DAYS';
      return this.translate.instant(`SETTINGS.${key}`, { count });
    }
    if (seconds % 3600 === 0) {
      const count = seconds / 3600;
      const key = count === 1 ? 'TASK_EVERY_HOUR' : 'TASK_EVERY_HOURS';
      return this.translate.instant(`SETTINGS.${key}`, { count });
    }
    const count = Math.max(1, Math.round(seconds / 60));
    return this.translate.instant('SETTINGS.TASK_EVERY_MINUTES', { count });
  }

  formatNextRunRelative(time?: string | null): string {
    if (!time) {
      return this.translate.instant('SETTINGS.TASK_NOT_SCHEDULED');
    }

    const next = new Date(time);
    const diffMs = next.getTime() - Date.now();
    if (Number.isNaN(next.getTime())) {
      return this.translate.instant('SETTINGS.TASK_NOT_SCHEDULED');
    }
    if (diffMs <= 0) {
      return this.translate.instant('SETTINGS.TASK_DUE');
    }

    const formatter = new Intl.RelativeTimeFormat(this.locale(), {
      numeric: 'always',
      style: 'long',
    });
    if (diffMs < 60 * 60 * 1000) {
      return formatter.format(Math.max(1, Math.ceil(diffMs / 60000)), 'minute');
    }
    if (diffMs < 24 * 60 * 60 * 1000) {
      return formatter.format(Math.ceil(diffMs / 3600000), 'hour');
    }
    return formatter.format(Math.ceil(diffMs / 86400000), 'day');
  }

  formatNextRunExact(time?: string | null): string {
    if (!time) {
      return '';
    }
    const next = new Date(time);
    if (Number.isNaN(next.getTime())) {
      return '';
    }
    return new Intl.DateTimeFormat(this.locale(), {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(next);
  }

  private resolveTaskId(job: JobInfo): string {
    return this.legacyJobIds[job.name] || job.id;
  }

  private taskTranslation(job: JobInfo, field: 'NAME' | 'DESCRIPTION'): string {
    const key = `SETTINGS.TASKS.${this.resolveTaskId(job)}.${field}`;
    const translated = this.translate.instant(key);
    return translated === key ? '' : translated;
  }

  private parseLegacyInterval(trigger: string): number | null {
    const match = trigger.match(
      /interval\[(?:(\d+)\s+days?,\s+)?(\d+):(\d+):(\d+)\]/
    );
    if (!match) {
      return null;
    }
    const days = Number(match[1] || 0);
    const hours = Number(match[2] || 0);
    const minutes = Number(match[3] || 0);
    const seconds = Number(match[4] || 0);
    return days * 86400 + hours * 3600 + minutes * 60 + seconds;
  }

  private locale(): string {
    const language = this.translate.currentLang || 'zh';
    if (language.startsWith('ja')) {
      return 'ja-JP';
    }
    if (language.startsWith('en')) {
      return 'en-US';
    }
    return 'zh-CN';
  }
}
