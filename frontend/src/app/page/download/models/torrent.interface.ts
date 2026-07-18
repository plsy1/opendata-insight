import { MovieData } from '../../../models/movie-data.interface';
import { FC2ProductionInformation } from '../../fc2-production-information/model/fc2-production.interface';

export interface DownloadingTorrent {
  hash: string;
  name: string;
  progress: number;
  size: number;
  download_speed: number;
  eta: number;
  tags: string;
  work_id?: string | null;
  media_type?: 'jav' | 'fc2' | null;
  movie?: MovieData | null;
  fc2_product?: FC2ProductionInformation | null;
}

export interface DeleteTorrentResult {
  status: 'success';
  hash: string;
  deleted_files: boolean;
}
