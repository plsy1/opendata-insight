export interface fc2RankingItem {
  term: string;
  page: number;
  rank: number;
  article_id: string;
  title: string;
  url: string;
  cover: string;
  owner: string;
  seller_id?: string | null;
  seller_url?: string | null;
  rating: number;
  comment_count: number;
  hot_comments: string[];
}

export enum RankingType {
  Realtime = "realtime",
  Daily = "daily",
  Weekly = "weekly",
  Monthly = "monthly",
  Yearly = "yearly"
}
