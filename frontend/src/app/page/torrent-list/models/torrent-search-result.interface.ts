export interface TorrentSearchResult {
  indexer?: string;
  title?: string;
  size?: number;
  seeders?: number;
  leechers?: number;
  publishDate?: string;
  infoUrl?: string;
  downloadUrl?: string;
  magnetUrl?: string;
  resolution?: string | null;
  codec?: string | null;

  // Local presentation state; it is never sent back to the API.
  loading?: boolean;
  error?: boolean;
  success?: boolean;

  // Preserve fields supplied by Prowlarr that this view does not currently use.
  [key: string]: unknown;
}
