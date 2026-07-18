import { MovieSubscriptionRules } from './subscription-rules.interface';

export interface MoviePoster {
  id: string;
  full_id: string;
  title: string;
  release_date: string;
  img_url: string;
  actors: string[];
}

export interface SampleImage {
  l?: string;
  s?: string;
  [key: string]: unknown;
}

export interface MoviePerson {
  name: string;
  id?: number;
  order?: number | null;
  image_url?: string | null;
  talent?: {
    id: number;
    deleted_at?: string | null;
  };
  ruby?: string;
  note?: string;
  [key: string]: unknown;
}

export interface MetadataTag {
  id?: number;
  canonical_id?: string;
  name: string;
  [key: string]: unknown;
}

export interface MovieProduct {
  id?: number | null;
  work_id?: number | null;
  product_id: string;
  url: string;
  image_url?: string | null;
  title: string;
  source?: string | null;
  thumbnail_url?: string | null;
  date?: string | null;
  maker?: string | null;
  label?: string | null;
  series?: string | null;
  sample_image_urls: SampleImage[];
  director?: string | null;
  price?: string | null;
  volume?: string | null;
  [key: string]: unknown;
}

export interface MovieSubscription {
  movie_id: number;
  is_downloaded: boolean;
  created_at?: string | null;
  rule_config?: Omit<MovieSubscriptionRules, 'use_global'> | null;
}

export interface MovieData {
  id?: number | null;
  work_id: string;
  prefix?: string | null;
  title: string;
  min_date?: string | null;
  casts: MoviePerson[];
  actors: MoviePerson[];
  tags: MetadataTag[];
  genres: string[];
  created_at?: string | null;
  source_type?: string | null;
  last_seen_at?: string | null;
  metadata_updated_at?: string | null;
  products: MovieProduct[];
  primary_product?: MovieProduct | null;
  subscribers?: MovieSubscription | null;
  [key: string]: unknown;
}

export interface MovieFeedItem extends MoviePoster {
  movie: MovieData;
  subscription_rules: MovieSubscriptionRules;
}

export interface MovieFeedPage {
  items: MovieFeedItem[];
  next_cursor: string | null;
  has_more: boolean;
  total: number;
}
