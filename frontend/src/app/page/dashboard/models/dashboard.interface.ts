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
  name: string;
  primary: string;
  primary_local:string;
  serverId: string;
  indexLink: string;
  playbackLink: string
  hideImage: boolean;
}

export interface ResumeItem {
  name: string;
  primary: string;
    primary_local:string;
  serverId: string;
  indexLink: string;
  playbackLink: string
  PlayedPercentage: number;
  ProductionYear?: number;
  hideImage: boolean;
}

export interface EmbyView {
  name: string;
  primary: string;
  primary_local: string;
  serverId: string;
  indexLink: string;
}