export interface fc2RankingItem {
  term: string;
  page: number;
  rank: number;
  article_id: string;
  title: string;
  url: string;
  cover: string;
  owner: string;
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