import { Component, OnInit } from '@angular/core';
import { SettingsService } from '../../service/settings.service';
import { JobInfo } from '../../models/job_info.interface';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { MatSnackBar } from '@angular/material/snack-bar';
@Component({
  selector: 'app-background-tasks',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    MatDividerModule,
  ],
  templateUrl: './background-tasks.component.html',
  styleUrl: './background-tasks.component.css',
})
export class BackgroundTasksComponent implements OnInit {
  jobs: JobInfo[] = [];
  displayedColumns = ['name', 'trigger', 'nextRunTime', 'action'];
  constructor(
    private SettingsService: SettingsService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadJobs();
  }

  run(job_id: string) {
    this.SettingsService.runBackgroundTask(job_id).subscribe({
      next: (res) => {
        this.snackBar.open('Run successfully', 'Close', { duration: 2000 });
        this.loadJobs();
      },
      error: (err) => {
        console.error('Run failed:', err);
      },
    });
  }

  loadJobs() {
    this.SettingsService.listBackgroundTasks().subscribe({
      next: (jobs) => {
        this.jobs = jobs;
      },
      error: (err) => {
        console.error('Load jobs failed:', err);
      },
    });
  }

  formatTrigger(trigger: string): string {
    if (!trigger.startsWith('interval[')) {
      return trigger;
    }

    const match = trigger.match(/interval\[(\d+):(\d+):(\d+)\]/);
    if (!match) {
      return trigger;
    }

    const [, h, m, s] = match.map(Number);

    const parts: string[] = [];
    if (h) parts.push(`${h}h`);
    if (m) parts.push(`${m}m`);
    if (s) parts.push(`${s}s`);

    return `Every ${parts.join(' ')}`;
  }

  formatNextRun(time?: string | null): string {
    if (!time) {
      return '-';
    }

    const now = new Date();
    const next = new Date(time);

    const diffMs = next.getTime() - now.getTime();
    if (diffMs <= 0) {
      return 'Due';
    }

    const diffMin = Math.floor(diffMs / 60000);
    const diffH = Math.floor(diffMin / 60);
    const diffM = diffMin % 60;

    if (diffH < 24) {
      const parts: string[] = [];
      if (diffH) parts.push(`${diffH}h`);
      if (diffM) parts.push(`${diffM}m`);
      return `in ${parts.join(' ')}`;
    }

    // 超过一天，显示具体时间
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    }).format(next);
  }
}
