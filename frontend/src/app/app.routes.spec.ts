import { APP_ROUTE_SEGMENTS } from './app-paths';
import { routes } from './app.routes';


describe('application routes', () => {
  const shell = routes.find((route) => route.path === '');
  const childRoutes = shell?.children ?? [];

  it('declares the canonical route set', () => {
    const paths = new Set(childRoutes.map((route) => route.path));
    const canonical = [
      APP_ROUTE_SEGMENTS.dashboard,
      APP_ROUTE_SEGMENTS.explore,
      APP_ROUTE_SEGMENTS.torrentSearch,
      APP_ROUTE_SEGMENTS.torrentSearchWithQuery,
      APP_ROUTE_SEGMENTS.movieSearch,
      APP_ROUTE_SEGMENTS.movieSearchWithQuery,
      APP_ROUTE_SEGMENTS.downloads,
      APP_ROUTE_SEGMENTS.performerSubscriptions,
      APP_ROUTE_SEGMENTS.movieSubscriptions,
      APP_ROUTE_SEGMENTS.performerDetail,
      APP_ROUTE_SEGMENTS.movieDetail,
      APP_ROUTE_SEGMENTS.fc2MovieDetail,
      APP_ROUTE_SEGMENTS.settings,
    ];

    for (const path of canonical) {
      expect(paths.has(path)).withContext(path).toBeTrue();
    }
  });

  it('keeps redirects for legacy bookmarks', () => {
    const legacyPaths = [
      'subscription/performer',
      'subscription/production',
      'torrents',
      'torrents/:value',
      'keywords',
      'keywords/:value',
      'download',
      'performer/:name',
      'production/fc2/:id',
      'production/:id',
    ];

    for (const path of legacyPaths) {
      const route = childRoutes.find((candidate) => candidate.path === path);
      expect(route?.redirectTo).withContext(path).toBeDefined();
    }
  });
});
