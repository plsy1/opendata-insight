export interface FC2ProductionInformation {
  id: number;
  article_id?: string | null;
  product_id?: string | null;
  cover?: string | null;
  duration?: string | null;
  title?: string | null;
  author?: string | null;
  sale_day?: string | null;
  sample_images: string[] | null;
  crawled_at?: string | null;
}
