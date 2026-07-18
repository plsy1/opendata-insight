export interface FC2ProductionInformation {
  id: number;
  article_id?: string | null;
  product_id?: string | null;
  cover?: string | null;
  duration?: string | null;
  title?: string | null;
  author?: string | null;
  seller_id?: string | null;
  seller_url?: string | null;
  sale_day?: string | null;
  description?: string | null;
  price?: string | null;
  rating?: number | null;
  comment_count?: number | null;
  favorite_count?: number | null;
  seller_page?: number | null;
  seller_position?: number | null;
  sample_images: string[] | null;
  crawled_at?: string | null;
}
