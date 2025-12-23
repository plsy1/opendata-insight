import { MovieInformation } from '../models/movie-information.interface';

export function createDefaultMovieInformation(): MovieInformation {
  return {
    props: {
      pageProps: {
        work: {
          id: 0,
          prefix: '',
          work_id: '',
          title: '',
          min_date: undefined,
          note: undefined,
          casts: [],
          actors: [],
          tags: [],
          genres: [],
          products: [],
        },
        editors: [],
        comments: [],
        children: [],
        parents: [],
        noindex: false,
        _sentryTraceData: undefined,
        _sentryBaggage: undefined,
      },
      __N_SSP: false,
    },
    page: '',
    query: {},
    buildId: '',
    runtimeConfig: {},
    isFallback: false,
    isExperimentalCompile: false,
    gssp: false,
    scriptLoader: [],
  };
}