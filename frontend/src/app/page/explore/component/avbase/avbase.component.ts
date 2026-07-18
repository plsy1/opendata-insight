import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import { MatTabsModule } from '@angular/material/tabs';
import { Router } from '@angular/router';
import { PageExploreServiceService } from '../../services/page-explore.service';
import { CommonModule } from '@angular/common';
import { AvbaseIndexData } from '../../models/page-explore';
import { MatIconModule } from '@angular/material/icon';
import { AvbaseEverydayReleaseByPrefix } from '../../models/avbase-everyday-release';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MovieCardComponent } from '../../../../shared/movie-card/movie-card.component';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatInputModule } from '@angular/material/input';
import { APP_PATHS } from '../../../../app-paths';

interface AvbaseViewState {
  currentDate: string;
  selectedMaker: string;
  releaseFilter: string;
  makersExpanded: boolean;
}

@Component({
  selector: 'app-avbase',
  standalone: true,
  imports: [
    MatTabsModule,
    MovieCardComponent,
    CommonModule,
    MatIconModule,
    MatTooltipModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatInputModule,
    FormsModule,
    TranslateModule,
  ],
  templateUrl: './avbase.component.html',
  styleUrl: './avbase.component.css',
})
export class AvbaseComponent implements OnInit, OnDestroy {
  private readonly maxRecentSearches = 30;
  private readonly viewStateKey = 'avbaseExploreViewState';
  private readonly filterHistoryKey = 'avbaseReleaseFilterHistory';

  currentDate: Date = new Date();
  avbaseIndexData?: AvbaseIndexData;
  releaseData: AvbaseEverydayReleaseByPrefix[] = [];
  filteredReleaseData: AvbaseEverydayReleaseByPrefix[] = [];
  selectedMaker = '';
  releaseFilter = '';
  makersExpanded = false;
  totalReleaseCount = 0;
  visibleReleaseCount = 0;
  filterHistoryOpen = false;
  searchKeywordHistory: string[] = [];

  constructor(
    public PageExploreService: PageExploreServiceService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.restoreViewState();
    this.loadFilterHistory();
    const cachedData = this.PageExploreService.getAvbaseIndexData();
    const cachedEveryReleaseData =
      this.PageExploreService.getAvbaseEverydayReleaseData();

    if (cachedData) {
      this.avbaseIndexData = cachedData;
    } else {
      this.loadAvbaseIndex();
    }

    if (cachedEveryReleaseData) {
      this.setReleaseData(cachedEveryReleaseData);
    } else {
      this.loadEverydayReleaseData();
    }
  }

  ngOnDestroy(): void {
    this.saveViewState();
  }

  get yyyymmdd(): string {
    return (
      this.currentDate.getFullYear().toString() +
      String(this.currentDate.getMonth() + 1).padStart(2, '0') +
      String(this.currentDate.getDate()).padStart(2, '0')
    );
  }

  loadAvbaseIndex(): void {
    this.PageExploreService.getAvbaseIndex().subscribe({
      next: (data) => {
        this.avbaseIndexData = data;
        this.PageExploreService.setAvbaseIndexData(data);
      },
      error: (err) => {
        console.error('Failed to load Avbase index:', err);
      },
    });
  }

  loadEverydayReleaseData() {
    this.PageExploreService.getAvbaseReleaseByDate(this.yyyymmdd).subscribe({
      next: (data: AvbaseEverydayReleaseByPrefix[]) => {
        this.setReleaseData(data);
        this.PageExploreService.setAvbaseEverydayReleaseData(data);
      },
      error: (err) => console.error('Error fetching daily release:', err),
    });
  }

  applyReleaseFilters(): void {
    const keyword = this.releaseFilter.trim().toLocaleLowerCase();
    this.filteredReleaseData = this.releaseData
      .filter((group) => !this.selectedMaker || group.maker === this.selectedMaker)
      .map((group) => ({
        ...group,
        works: keyword
          ? group.works.filter((work) =>
              [
                group.maker,
                work.id,
                work.full_id,
                work.title,
                work.release_date,
                ...work.actors,
              ]
                .join(' ')
                .toLocaleLowerCase()
                .includes(keyword)
            )
          : group.works,
      }))
      .filter((group) => group.works.length > 0);
    this.visibleReleaseCount = this.filteredReleaseData.reduce(
      (total, group) => total + group.works.length,
      0
    );
    this.saveViewState();
  }

  selectMaker(maker: string): void {
    this.selectedMaker = maker;
    this.applyReleaseFilters();
  }

  clearReleaseFilter(): void {
    this.releaseFilter = '';
    this.applyReleaseFilters();
    this.openFilterHistory();
  }

  get visibleFilterHistory(): string[] {
    const keyword = this.releaseFilter.trim().toLocaleLowerCase();
    return this.searchKeywordHistory
      .filter(
        (option) =>
          !keyword || option.toLocaleLowerCase().includes(keyword)
      )
      .slice(0, 10);
  }

  openFilterHistory(): void {
    this.loadFilterHistory();
    this.filterHistoryOpen = true;
  }

  closeFilterHistory(): void {
    this.commitReleaseFilter();
    this.filterHistoryOpen = false;
  }

  commitReleaseFilter(): void {
    const value = this.releaseFilter.trim();
    if (!value) return;

    const normalized = value.toLocaleLowerCase();
    this.searchKeywordHistory = [
      value,
      ...this.searchKeywordHistory.filter(
        (option) => option.toLocaleLowerCase() !== normalized
      ),
    ].slice(0, this.maxRecentSearches);
    this.saveFilterHistory();
    this.filterHistoryOpen = false;
  }

  selectFilterHistory(option: string): void {
    this.releaseFilter = option;
    this.applyReleaseFilters();
    this.commitReleaseFilter();
  }

  removeFilterHistory(option: string, event: Event): void {
    event.stopPropagation();
    this.searchKeywordHistory = this.searchKeywordHistory.filter(
      (value) => value !== option
    );
    this.saveFilterHistory();
  }

  trackFilterHistory(_index: number, option: string): string {
    return option;
  }

  toggleMakers(): void {
    this.makersExpanded = !this.makersExpanded;
    this.saveViewState();
  }

  trackMaker(_index: number, group: AvbaseEverydayReleaseByPrefix): string {
    return group.maker;
  }

  trackWork(_index: number, work: { id: string }): string {
    return work.id;
  }

  private setReleaseData(data: AvbaseEverydayReleaseByPrefix[]): void {
    this.releaseData = data;
    this.totalReleaseCount = data.reduce(
      (total, group) => total + group.works.length,
      0
    );
    if (
      this.selectedMaker &&
      !data.some((group) => group.maker === this.selectedMaker)
    ) {
      this.selectedMaker = '';
    }
    this.applyReleaseFilters();
  }

  private loadFilterHistory(): void {
    const saved = localStorage.getItem(this.filterHistoryKey);
    if (!saved) {
      this.searchKeywordHistory = [];
      return;
    }

    try {
      const parsed = JSON.parse(saved);
      this.searchKeywordHistory = Array.isArray(parsed)
        ? parsed
            .filter((option): option is string => typeof option === 'string')
            .slice(0, this.maxRecentSearches)
        : [];
    } catch {
      localStorage.removeItem(this.filterHistoryKey);
      this.searchKeywordHistory = [];
    }
  }

  private saveFilterHistory(): void {
    localStorage.setItem(
      this.filterHistoryKey,
      JSON.stringify(this.searchKeywordHistory)
    );
  }

  async cardClick(name: string) {
    try {
      this.router.navigate([APP_PATHS.performers, name]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  async posterClick(work_id: string) {
    try {
      this.router.navigate([APP_PATHS.movies, work_id]);
    } catch (error) {
      console.error('Failed:', error);
    }
  }

  prevDay() {
    this.currentDate = new Date(this.currentDate);
    this.currentDate.setDate(this.currentDate.getDate() - 1);
    this.makersExpanded = false;
    this.saveViewState();

    this.loadEverydayReleaseData();
  }

  nextDay() {
    this.currentDate = new Date(this.currentDate);
    this.currentDate.setDate(this.currentDate.getDate() + 1);
    this.makersExpanded = false;
    this.saveViewState();

    this.loadEverydayReleaseData();
  }

  onDateChange(event: any) {
    if (event.value) {
      this.currentDate = new Date(event.value);
      this.makersExpanded = false;
      this.saveViewState();
      this.loadEverydayReleaseData();
    }
  }

  private restoreViewState(): void {
    const saved = sessionStorage.getItem(this.viewStateKey);
    if (!saved) return;

    try {
      const state = JSON.parse(saved) as Partial<AvbaseViewState>;
      const dateMatch = String(state.currentDate || '').match(
        /^(\d{4})-(\d{2})-(\d{2})$/
      );
      if (dateMatch) {
        this.currentDate = new Date(
          Number(dateMatch[1]),
          Number(dateMatch[2]) - 1,
          Number(dateMatch[3])
        );
      }
      this.selectedMaker = String(state.selectedMaker || '');
      this.releaseFilter = String(state.releaseFilter || '');
      this.makersExpanded = state.makersExpanded === true;
    } catch {
      sessionStorage.removeItem(this.viewStateKey);
    }
  }

  private saveViewState(): void {
    const state: AvbaseViewState = {
      currentDate: [
        this.currentDate.getFullYear(),
        String(this.currentDate.getMonth() + 1).padStart(2, '0'),
        String(this.currentDate.getDate()).padStart(2, '0'),
      ].join('-'),
      selectedMaker: this.selectedMaker,
      releaseFilter: this.releaseFilter,
      makersExpanded: this.makersExpanded,
    };
    sessionStorage.setItem(this.viewStateKey, JSON.stringify(state));
  }
}
