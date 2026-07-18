export interface SubscriptionQualityRule {
  resolution: string | null;
  codec: string | null;
  required_keywords: string[];
  any_keywords: string[];
  excluded_keywords: string[];
  title_regex: string;
}

export interface MovieSubscriptionRules {
  use_global: boolean;
  global_excluded_keywords: string[];
  quality_rules: SubscriptionQualityRule[];
}
