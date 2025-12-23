import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { NgxEchartsModule } from 'ngx-echarts';
import { MatIconModule } from '@angular/material/icon';
import { DashboardService } from './../../service/dashboard.service';
import { StatAllResponse } from '../../models/statistic.interface';

@Component({
  selector: 'app-download-statistic',
  standalone: true,
  imports: [CommonModule, MatCardModule, NgxEchartsModule,MatIconModule],
  templateUrl: './download-statistic.component.html',
  styleUrl: './download-statistic.component.css',
})
export class DownloadStatisticComponent implements OnInit {
  statisticData: StatAllResponse | null = null;

  dailyChartOptions: any;
  studioChartOptions: any;
  actorChartOptions: any;

  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.dashboardService.getAllStatistic().subscribe({
      next: (data: StatAllResponse) => {
        this.statisticData = data;

        this.initDailyChart(data);
        this.initStudioChart(data);
        this.initActorChart(data);
      },
      error: (err) => {
        console.error('Failed to load Download Statistic data.', err);
      },
    });
  }

  // ===============================
  // Daily Download Chart
  // ===============================
  initDailyChart(data: StatAllResponse): void {
    this.dailyChartOptions = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: data.daily.map(d => d.date),
      },
      yAxis: {
        type: 'value',
      },
      series: [
        {
          name: 'Downloads',
          type: 'line',
          smooth: true,
          data: data.daily.map(d => d.count),
        },
      ],
    };
  }

  // ===============================
  // Top Studio Chart
  // ===============================
  initStudioChart(data: StatAllResponse): void {
    this.studioChartOptions = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: data.studio.map(s => s.studio),
      },
      yAxis: {
        type: 'value',
      },
      series: [
        {
          name: 'Downloads',
          type: 'bar',
          data: data.studio.map(s => s.count),
        },
      ],
    };
  }

  // ===============================
  // Top Actor Chart
  // ===============================
  initActorChart(data: StatAllResponse): void {
    this.actorChartOptions = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: data.actors.map(a => a.actor),
        axisLabel: {
          rotate: 30,
        },
      },
      yAxis: {
        type: 'value',
      },
      series: [
        {
          name: 'Downloads',
          type: 'bar',
          data: data.actors.map(a => a.count),
        },
      ],
    };
  }
}