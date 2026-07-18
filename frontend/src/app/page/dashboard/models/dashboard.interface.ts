export interface EmbyItemCounts {
  MovieCount: number;
  SeriesCount: number;
  EpisodeCount: number;
  GameCount: number;
  ArtistCount: number;
  ProgramCount: number;
  GameSystemCount: number;
  TrailerCount: number;
  SongCount: number;
  AlbumCount: number;
  MusicVideoCount: number;
  BoxSetCount: number;
  BookCount: number;
  ItemCount: number;
}

export interface EmbyLatestItem {
  name: string | null;
  primary: string;
  primary_local?: string;
  serverId: string | null;
  indexLink: string;
  playbackLink?: string | null;
  hideImage?: boolean;
}

export interface ResumeItem {
  name: string | null;
  primary: string;
  primary_local?: string;
  serverId: string | null;
  indexLink: string;
  playbackLink?: string | null;
  PlayedPercentage?: number;
  ProductionYear?: number;
  hideImage?: boolean;
}

export interface EmbyView {
  name: string | null;
  primary: string;
  primary_local?: string;
  serverId: string | null;
  indexLink: string;
  hideImage?: boolean;
}

export interface EmbyExistsResponse {
  exists: boolean;
  indexLink: string | null;
}
