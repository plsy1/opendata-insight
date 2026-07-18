import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { NgxEchartsModule } from 'ngx-echarts';
import { MatIconModule } from '@angular/material/icon';
import { DashboardService } from './../../service/dashboard.service';
import { TranslateModule } from '@ngx-translate/core';
import {
  StatAllResponse,
  StatNamedItem,
} from '../../models/statistic.interface';
import { Router } from '@angular/router';
import { APP_PATHS } from '../../../../app-paths';

@Component({
  selector: 'app-download-statistic',
  standalone: true,
  imports: [CommonModule, MatCardModule, NgxEchartsModule,MatIconModule, TranslateModule],
  templateUrl: './download-statistic.component.html',
  styleUrl: './download-statistic.component.css',
})
export class DownloadStatisticComponent implements OnInit {
  statisticData: StatAllResponse | null = null;

  dailyChartOptions: any;
  metadataRankings: Array<{
    titleKey: string;
    icon: string;
    items: StatNamedItem[];
  }> = [];

  constructor(
    private dashboardService: DashboardService,
    private router: Router
  ) {}

  goActor(name: string): void {
    this.router.navigate([APP_PATHS.performers, name]);
  }

  goMetadata(name: string): void {
    this.router.navigate([APP_PATHS.movieSearch, name]);
  }


  ngOnInit(): void {
    this.dashboardService.getAllStatistic().subscribe({
      next: (data: StatAllResponse) => {
        this.statisticData = data;

        this.initDailyChart(data);
        this.metadataRankings = [
          {
            titleKey: 'DASHBOARD.MAKER_RANKING',
            icon: 'factory',
            items: data.makers,
          },
          {
            titleKey: 'DASHBOARD.LABEL_RANKING',
            icon: 'sell',
            items: data.labels,
          },
          {
            titleKey: 'DASHBOARD.SERIES_RANKING',
            icon: 'collections_bookmark',
            items: data.series,
          },
          {
            titleKey: 'DASHBOARD.TAXONOMY_RANKING',
            icon: 'category',
            items: data.taxonomy,
          },
        ];
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
        top: 16,
        left: 12,
        right: 12,
        bottom: 24,
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
          margin: 8,
          hideOverlap: true,
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
          symbolSize: 5,
          itemStyle: { color: '#007bff' },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(0, 123, 255, 0.2)' },
                { offset: 1, color: 'rgba(0, 123, 255, 0)' },
              ],
            },
          },
          lineStyle: { width: 3, color: '#007bff' },
          data: data.daily.map(d => d.count),
        },
      ],
    };
  }

}
