export interface MovieProduct {
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
  sample_image_urls: { [key: string]: any }[];
  director?: string | null;
  price?: string | null;
  volume?: string | null;
}

interface Cast {
  id: number;
  name: string;
  order: number | null;
  image_url: string;
  talent: {
    id: number;
    deleted_at: string | null;
  };
  ruby: string;
  note: string;
}

export interface MovieData {
  work_id: string;
  prefix?: string | null;
  title: string;
  min_date?: string | null;
  casts: Cast[];
  actors: Cast[];
  tags: string[];
  genres: string[];
  created_at?: string | null;
  products: MovieProduct[];
}
