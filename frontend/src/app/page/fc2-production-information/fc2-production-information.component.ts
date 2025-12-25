import { Component, OnInit } from '@angular/core';
import { fc2ProductionService } from './services/fc2-productrion.services';
import { FC2ProductionInformation } from './model/fc2-production.interface';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';

import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { MatIconModule } from '@angular/material/icon';

import { Router } from '@angular/router';

@Component({
  selector: 'app-fc2-production-information',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatIconModule,
  ],
  templateUrl: './fc2-production-information.component.html',
  styleUrl: './fc2-production-information.component.css',
})
export class Fc2ProductionInformationComponent implements OnInit {
  data: FC2ProductionInformation | null = null;
  work_id: string = '';
  constructor(
    private fc2ProductionService: fc2ProductionService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe((params) => {
      this.work_id = params.get('id') || '';
      this.loadProductionData();
    });
  }

  loadProductionData(): void {
    this.fc2ProductionService
      .getFC2ProductionInformation(this.work_id)
      .subscribe({
        next: (data) => {
          this.data = data;
        },
        error: (error) => {
          console.error('Failed to load fc2 data:', error);
        },
      });
  }

  onWheelScroll(event: WheelEvent) {
    const container = event.currentTarget as HTMLElement;
    event.preventDefault();
    container.scrollLeft += event.deltaY;
  }

  async onSearchClick() {
    try {
      this.router.navigate(['/torrents', this.data?.article_id]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  async toSupjav() {
    try {
      window.open(`https://supjav.com/?s=${this.data?.article_id}`, '_blank');
    } catch (error) {
      console.error('Failed:', error);
    }
  }
  async toMissAV() {
    try {
      const lowerName = this.data?.product_id?.toLowerCase();
      window.open(`https://missav.ai/${lowerName}`, '_blank');
    } catch (error) {
      console.error('Failed:', error);
    }
  }
  async onSubscribeClick() {
    
  }
}
