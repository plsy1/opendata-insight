import { MovieData } from '../../../models/movie-data.interface';

export interface DownloadingTorrent {
  hash: string;
  name: string;
  progress: number;
  size: number;
  download_speed: number;
  eta: number;
  tags: string;
  work_id?: string | null;
  movie?: MovieData | null;
}

export interface DeleteTorrentResult {
  status: 'success';
  hash: string;
  deleted_files: boolean;
}
