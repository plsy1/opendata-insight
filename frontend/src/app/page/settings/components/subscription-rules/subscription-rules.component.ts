import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { MovieFeedItem } from '../../../../models/movie-data.interface';
import {
  MovieSubscriptionRules,
  SubscriptionQualityRule,
} from '../../../../models/subscription-rules.interface';
import { ProductionSubscriptionService } from '../../../production-subscription/service/production-subscription.service';
import { EnvironmentConfig } from '../../models/settings.interface';
import { SettingsService } from '../../service/settings.service';

interface EditableSubscriptionRule {
  resolution: string | null;
  codec: string | null;
  requiredKeywords: string;
  anyKeywords: string;
  excludedKeywords: string;
  titleRegex: string;
}

export interface MovieSubscriptionRulesDialogData {
  movie: MovieFeedItem;
}

@Component({
  selector: 'app-subscription-rules',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatSlideToggleModule,
    TranslateModule,
  ],
  templateUrl: './subscription-rules.component.html',
  styleUrl: './subscription-rules.component.css',
})
export class SubscriptionRulesComponent implements OnInit {
  private readonly dialogData = inject<MovieSubscriptionRulesDialogData | null>(
    MAT_DIALOG_DATA,
    { optional: true }
  );
  private readonly dialogRef = inject<
    MatDialogRef<SubscriptionRulesComponent> | null
  >(MatDialogRef, { optional: true });

  globalExcludedKeywords = '';
  subscriptionRules: EditableSubscriptionRule[] = [];
  isLoading = true;
  useGlobalRules = true;

  readonly resolutionOptions = [
    { value: '4320p', label: '8K / 4320p' },
    { value: '2160p', label: '4K / UHD / 2160p' },
    { value: '1440p', label: '2K / QHD / 1440p' },
    { value: '1080p', label: 'Full HD / 1080p' },
    { value: '1080i', label: '1080i' },
    { value: '720p', label: '720p' },
    { value: '576p', label: '576p' },
    { value: '480p', label: '480p' },
  ];

  readonly codecOptions = [
    { value: 'av1', label: 'AV1' },
    { value: 'h265', label: 'H.265 / HEVC / x265' },
    { value: 'h264', label: 'H.264 / AVC / x264' },
    { value: 'vp9', label: 'VP9' },
    { value: 'mpeg2', label: 'MPEG-2' },
  ];

  constructor(
    private settingsService: SettingsService,
    private productionSubscriptionService: ProductionSubscriptionService,
    private snackBar: MatSnackBar,
    private translate: TranslateService
  ) {}

  get isMovieMode(): boolean {
    return !!this.dialogData?.movie;
  }

  get movie(): MovieFeedItem | null {
    return this.dialogData?.movie || null;
  }

  ngOnInit(): void {
    this.settingsService.getEnvironment().subscribe({
      next: (data: EnvironmentConfig) => {
        const movieRules = this.movie?.subscription_rules;
        this.useGlobalRules = movieRules?.use_global ?? true;

        const globalExcluded =
          this.isMovieMode && !this.useGlobalRules
            ? movieRules?.global_excluded_keywords || []
            : data.SUBSCRIBE_GLOBAL_EXCLUDED || [];
        const qualityRules =
          this.isMovieMode && !this.useGlobalRules
            ? movieRules?.quality_rules || []
            : data.SUBSCRIBE_QUALITY_RULES || [];

        this.loadEditableRules(globalExcluded, qualityRules);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading subscription rules:', error);
        this.isLoading = false;
        this.showSaveError();
      },
    });
  }

  addQualityRule(): void {
    this.subscriptionRules.push({
      resolution: null,
      codec: null,
      requiredKeywords: '',
      anyKeywords: '',
      excludedKeywords: '',
      titleRegex: '',
    });
  }

  removeQualityRule(index: number): void {
    this.subscriptionRules.splice(index, 1);
  }

  moveQualityRule(index: number, direction: -1 | 1): void {
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= this.subscriptionRules.length) {
      return;
    }

    const [rule] = this.subscriptionRules.splice(index, 1);
    this.subscriptionRules.splice(targetIndex, 0, rule);
  }

  saveRules(): void {
    const qualityRules = this.serializeQualityRules();

    if (this.isMovieMode && this.movie) {
      const payload: MovieSubscriptionRules = {
        use_global: this.useGlobalRules,
        global_excluded_keywords: this.parseKeywords(
          this.globalExcludedKeywords
        ),
        quality_rules: qualityRules,
      };
      this.productionSubscriptionService
        .updateMovieSubscriptionRules(this.movie.id, payload)
        .subscribe({
          next: () => this.handleSaveSuccess(),
          error: (error) => {
            console.error('Error saving movie subscription rules:', error);
            this.showSaveError();
          },
        });
      return;
    }

    const payload: Partial<EnvironmentConfig> = {
      SUBSCRIBE_GLOBAL_EXCLUDED: this.parseKeywords(
        this.globalExcludedKeywords
      ),
      SUBSCRIBE_QUALITY_RULES: qualityRules,
    };

    this.settingsService.updateEnvironment(payload).subscribe({
      next: () => this.handleSaveSuccess(),
      error: (error) => {
        console.error('Error saving subscription rules:', error);
        this.showSaveError();
      },
    });
  }

  closeDialog(): void {
    this.dialogRef?.close(false);
  }

  private loadEditableRules(
    globalExcludedKeywords: string[],
    qualityRules: SubscriptionQualityRule[]
  ): void {
    this.globalExcludedKeywords = globalExcludedKeywords.join(', ');
    this.subscriptionRules = qualityRules.map((rule) => ({
      resolution: rule.resolution || null,
      codec: rule.codec || null,
      requiredKeywords: (rule.required_keywords || []).join(', '),
      anyKeywords: (rule.any_keywords || []).join(', '),
      excludedKeywords: (rule.excluded_keywords || []).join(', '),
      titleRegex: rule.title_regex || '',
    }));
  }

  private serializeQualityRules(): SubscriptionQualityRule[] {
    return this.subscriptionRules.map((rule) => ({
      resolution: rule.resolution,
      codec: rule.codec,
      required_keywords: this.parseKeywords(rule.requiredKeywords),
      any_keywords: this.parseKeywords(rule.anyKeywords),
      excluded_keywords: this.parseKeywords(rule.excludedKeywords),
      title_regex: rule.titleRegex.trim(),
    }));
  }

  private parseKeywords(value: string): string[] {
    return value
      .split(/[,，;；\n]/)
      .map((keyword) => keyword.trim())
      .filter(
        (keyword, index, values) =>
          !!keyword && values.indexOf(keyword) === index
      );
  }

  private handleSaveSuccess(): void {
    const messageKey = this.isMovieMode
      ? 'SETTINGS.MOVIE_SUBSCRIBE_RULES_SAVED'
      : 'SETTINGS.SUBSCRIBE_RULES_SAVED';
    this.snackBar.open(
      this.translate.instant(messageKey),
      this.translate.instant('COMMON.CLOSE'),
      {
        duration: 3000,
        panelClass: ['success-snackbar'],
      }
    );
    this.dialogRef?.close(true);
  }

  private showSaveError(): void {
    const messageKey = this.isMovieMode
      ? 'SETTINGS.MOVIE_SUBSCRIBE_RULES_SAVE_FAILED'
      : 'SETTINGS.SUBSCRIBE_RULES_SAVE_FAILED';
    this.snackBar.open(
      this.translate.instant(messageKey),
      this.translate.instant('COMMON.CLOSE'),
      {
        duration: 3000,
        panelClass: ['error-snackbar'],
      }
    );
  }
}
