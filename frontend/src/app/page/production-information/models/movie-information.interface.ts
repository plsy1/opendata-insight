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
  thumbnail_url: string;
  date?: string | null;
  maker?: MakerLabelSeries | null;
  label?: MakerLabelSeries | null;
  series?: MakerLabelSeries | null;
  sample_image_urls: Record<string, any>[];
  iteminfo?: ProductItemInfo | null;
}

export interface Genre {
  id: number;
  name: string;
  canonical_id?: string | number | null;
}

export interface Work {
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

export interface AvbaseEverydayReleaseByPrefix {
  prefixName: string;
  works: Work[];
}

export interface PageProps {
  work: Work;
  editors: any[];
  comments: any[];
  children: any[];
  parents: any[];
  noindex: boolean;
  _sentryTraceData?: string | null;
  _sentryBaggage?: string | null;
}

export interface Props {
  pageProps: PageProps;
  __N_SSP: boolean;
}

export interface MovieInformation {
  props: Props;
  page: string;
  query: Record<string, any>;
  buildId: string;
  runtimeConfig: Record<string, any>;
  isFallback: boolean;
  isExperimentalCompile: boolean;
  gssp: boolean;
  scriptLoader: any[];
}