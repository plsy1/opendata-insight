export interface ActressRanking {
  rank: string | null;
  name: string | null;
  image: string | null;
  profile_url: string | null;
  latest_work: string | null;
  latest_work_url: string | null;
  work_count: number;
  [key: string]: unknown;
}

export interface RankingItem {
  rank: string | null;
  title: string | null;
  number: string | null;
  image: string | null;
  detail_url: string | null;
  maker: string | null;
  actresses: string[];
  [key: string]: unknown;
}

export enum RankingTypeOfWorks {
  Daily = 'daily',
  Weekly = 'weekly',
  Monthly = 'monthly',
}

export interface Product {
  id: number;
  product_id: string;
  url: string;
  image_url: string;
  title: string;
  source: string;
  thumbnail_url: string;
  date: string;
  maker: {
    name: string;
  };
  label: {
    name: string;
  };
  series: {
    name: string;
  };
  sample_image_urls: {
    s: string;
    l: string;
  }[];
  iteminfo: {
    description: string;
    price: string;
    volume: string;
    campaign?: {
      price: number;
      list_price: number;
      end: string;
    };
  };
}

export interface Talent {
  primary: Primary;
  profile: any | null;
  deleted_at: string | null;
  meta: any | null;
}

export interface Primary {
  id: number;
  name: string;
  name_length: number;
  ruby: string;
  url: string;
  image_url: string;
  note: string;
  order: number | null;
  fanza_id: number | null;
  talent_id: number;
  meta: PrimaryMeta;
  created_at: string;
  updated_at: string;
}

export interface PrimaryMeta {
  fanza: Fanza;
}

export interface Fanza {
  id: string;
  hip: number | null;
  bust: number | null;
  name: string;
  ruby: string;
  hobby: string;
  waist: number | null;
  height: number | null;
  listURL: ListURL;
  birthday: string | null;
  imageURL: ImageURL;
  blood_type: string | null;
  prefectures: string;
}

export interface ListURL {
  mono: string;
  digital: string;
  monthly: string;
}

export interface ImageURL {
  large: string;
  small: string;
}

export interface AvbaseIndexData {
  newbie_talents: avbaseIndexTalent[];
  popular_talents: avbaseIndexTalent[];
}

export interface avbaseIndexTalent {
  name: string;
  id?: number | null;
  avatar_url: string | null;
}
