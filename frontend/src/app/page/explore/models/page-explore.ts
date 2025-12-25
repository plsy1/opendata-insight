export interface ActressRanking {
  rank: string;
  name: string;
  image: string;
  profile_url: string;
  latest_work: string;
  latest_work_url: string;
  work_count: number;
}

export interface RankingItem {
  rank: string;
  title: string;
  number: string;
  image: string;
  detail_url: string;
  maker: string | null;
  actresses: string[];
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

export interface JavtrailersVideo {
  contentId: string;
  dvdId: string;
  releaseDate: string;
  image: string;
}

export interface JavtrailersStudio {
  name: string;
  jpName: string;
  slug: string;
  link: string;
  videos: JavtrailersVideo[];
}

export interface JavtrailersDailyRelease {
  date: string;
  year: number;
  month: number;
  day: number;
  totalVideos: number;
  studios: JavtrailersStudio[];
}

export interface AvbaseIndexData {
  newbie_talents: avbaseIndexTalent[];
  popular_talents: avbaseIndexTalent[];
}

export interface avbaseIndexTalent {
  name: string;
  id: number;
  avatar_url: string;
}
