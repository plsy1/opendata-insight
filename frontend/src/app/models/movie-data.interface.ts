export interface Talent {
  id: number;
  deleted_at?: string | null;
}

export interface Actor {
  id: number;
  name: string;
  order?: number | null;
  image_url?: string | null;
  talent?: Talent | null;
  ruby?: string | null;
  note?: string | null;
}

export interface Cast {
  actor: Actor;
  note?: string | null;
}

export interface Genre {
  id: number;
  name: string;
  canonical_id?: string | number | null;
}

export interface MakerLabelSeries {
  name: string;
}

export interface ProductItemInfo {
  director?: string | null;
  price?: string | null;
  volume?: string | null;
}

export interface Product {
  id: number;
  product_id: string;
  url: string;
  image_url?: string | null;
  title: string;
  source?: string | null;
  thumbnail_url?: string | null;
  date?: string | null;
  maker?: MakerLabelSeries | null;
  label?: MakerLabelSeries | null;
  series?: MakerLabelSeries | null;
  sample_image_urls: Record<string, any>[];
  iteminfo?: ProductItemInfo | null;
}

export interface MovieData {
  id: number;
  prefix: string;
  work_id: string;
  title: string;
  min_date?: string | null;
  note?: string | null;
  casts: Cast[];
  actors: Actor[];
  tags: any[];
  genres: Genre[];
  products: Product[];
}
