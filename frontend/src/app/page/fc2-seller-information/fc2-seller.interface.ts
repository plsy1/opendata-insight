import { FC2ProductionInformation } from '../fc2-production-information/model/fc2-production.interface';

export interface FC2SellerProfile {
  id: number;
  seller_id: string;
  author_id: string;
  name: string;
  profile_url: string;
  avatar_url?: string | null;
  banner_url?: string | null;
  short_intro?: string | null;
  description?: string | null;
  product_count?: number | null;
  follower_count?: number | null;
  crawled_at?: string | null;
}

export interface FC2SellerWorksResponse {
  seller: FC2SellerProfile;
  works: FC2ProductionInformation[];
  page: number;
  total: number;
  has_next: boolean;
}
