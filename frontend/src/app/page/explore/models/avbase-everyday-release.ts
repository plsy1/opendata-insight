export interface MoviePoster {
  id: string;
  full_id: string
  title: string;
  release_date: string;
  img_url: string;
  actors: string[];
}

export interface AvbaseEverydayReleaseByPrefix {
  maker: string;
  works: MoviePoster[];
}
