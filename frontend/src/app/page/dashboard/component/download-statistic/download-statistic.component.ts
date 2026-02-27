import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { NgxEchartsModule } from 'ngx-echarts';
import { MatIconModule } from '@angular/material/icon';
import { DashboardService } from './../../service/dashboard.service';
import { StatAllResponse } from '../../models/statistic.interface';
import { Router } from '@angular/router';

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

  constructor(
    private dashboardService: DashboardService,
    private router: Router
  ) {}

  goActor(name: string): void {
    this.router.navigate(['/performer', name]);
  }

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
      grid: {
        top: '15%',
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true,
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        borderColor: '#007bff',
        textStyle: { color: '#fff' },
      },
      xAxis: {
        type: 'category',
        data: data.daily.map(d => d.date),
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
        axisLabel: { 
          color: '#8a8a8a', 
          fontSize: 10,
          margin: 12
        },
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
        axisLabel: { color: '#8a8a8a' },
      },
      series: [
        {
          name: 'Downloads',
          type: 'line',
          smooth: true,
          symbolSize: 8,
          itemStyle: { color: '#007bff' },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(0, 123, 255, 0.3)' },
                { offset: 1, color: 'rgba(0, 123, 255, 0)' },
              ],
            },
          },
          lineStyle: { width: 4, color: '#007bff' },
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