import { SubscriptionQualityRule } from '../../../models/subscription-rules.interface';

export type { SubscriptionQualityRule } from '../../../models/subscription-rules.interface';

export interface EnvironmentConfig {
  PROWLARR_URL: string;
  PROWLARR_KEY: string;
  DOWNLOAD_PATH: string;
  JAV_DOWNLOAD_PATH: string;
  FC2_DOWNLOAD_PATH: string;

  QB_URL: string;
  QB_USERNAME: string;
  QB_PASSWORD: string;
  QB_KEYWORD_FILTER: string[];

  SUBSCRIBE_GLOBAL_EXCLUDED: string[];
  SUBSCRIBE_QUALITY_RULES: SubscriptionQualityRule[];

  TELEGRAM_TOKEN: string;
  TELEGRAM_CHAT_ID: string;

  EMBY_URL: string;
  EMBY_API_KEY: string;
}
