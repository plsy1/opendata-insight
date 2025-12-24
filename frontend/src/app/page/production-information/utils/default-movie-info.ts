import { MovieData } from '../models/movie-data.interface';

export function createDefaultMovieInformation(): MovieData {
  return {
    work_id: '',
    prefix: '',
    title: '',
    min_date: null,
    casts: [],
    actors: [],
    tags: [],
    genres: [],
    created_at: null,
    products: [],
  };
}