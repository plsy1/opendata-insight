export interface StatOverview {
  total: number;
  downloaded: number;
  not_downloaded: number;
}

export interface StatDailyItem {
  date: string;
  count: number;
}

export interface StatStudioItem {
  studio: string;
  count: number;
}

export interface StatActorItem {
  actor: string;
  count: number;
}

export interface StatAllResponse {
  overview: StatOverview;
  daily: StatDailyItem[];
  studio: StatStudioItem[];
  actors: StatActorItem[];
}