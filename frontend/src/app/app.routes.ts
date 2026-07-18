import { Routes } from '@angular/router';
import { APP_ROUTE_SEGMENTS } from './app-paths';
import { authGuard } from './guards/auth.guard';
import { DashboardComponent } from './page/dashboard/dashboard.component';
import { DownloadComponent } from './page/download/download.component';
import { ExploreComponent } from './page/explore/explore.component';
import { Fc2ProductionInformationComponent } from './page/fc2-production-information/fc2-production-information.component';
import { HomeComponent } from './page/home/home.component';
import { KeywordsSearchComponent } from './page/keywords-search/keywords-search.component';
import { LoginComponent } from './page/login/login.component';
import { PerformerInformationComponent } from './page/performer-information/performer-information.component';
import { PerformerSubscriptionComponent } from './page/performer-subscription/performer-subscription.component';
import { ProductionInformationComponent } from './page/production-information/production-information.component';
import { ProductionSubscriptionComponent } from './page/production-subscription/production-subscription.component';
import { SettingsComponent } from './page/settings/settings.component';
import { TorrentListComponent } from './page/torrent-list/torrent-list.component';


export const routes: Routes = [
  {
    path: '',
    component: HomeComponent,
    canActivate: [authGuard],
    canActivateChild: [authGuard],
    children: [
      {
        path: '',
        redirectTo: APP_ROUTE_SEGMENTS.dashboard,
        pathMatch: 'full',
      },
      { path: APP_ROUTE_SEGMENTS.dashboard, component: DashboardComponent },
      { path: APP_ROUTE_SEGMENTS.explore, component: ExploreComponent },
      { path: APP_ROUTE_SEGMENTS.settings, component: SettingsComponent },
      {
        path: APP_ROUTE_SEGMENTS.performerSubscriptions,
        component: PerformerSubscriptionComponent,
      },
      {
        path: APP_ROUTE_SEGMENTS.movieSubscriptions,
        component: ProductionSubscriptionComponent,
      },
      {
        path: APP_ROUTE_SEGMENTS.torrentSearch,
        component: TorrentListComponent,
      },
      {
        path: APP_ROUTE_SEGMENTS.torrentSearchWithQuery,
        component: TorrentListComponent,
      },
      {
        path: APP_ROUTE_SEGMENTS.movieSearch,
        component: KeywordsSearchComponent,
      },
      {
        path: APP_ROUTE_SEGMENTS.movieSearchWithQuery,
        component: KeywordsSearchComponent,
      },
      { path: APP_ROUTE_SEGMENTS.downloads, component: DownloadComponent },
      {
        path: APP_ROUTE_SEGMENTS.performerDetail,
        component: PerformerInformationComponent,
      },
      {
        path: APP_ROUTE_SEGMENTS.fc2MovieDetail,
        component: Fc2ProductionInformationComponent,
      },
      {
        path: APP_ROUTE_SEGMENTS.movieDetail,
        component: ProductionInformationComponent,
      },

      // Compatibility redirects for links and bookmarks created before v1.0.18.
      { path: 'subscription/performer', redirectTo: APP_ROUTE_SEGMENTS.performerSubscriptions },
      { path: 'subscription/production', redirectTo: APP_ROUTE_SEGMENTS.movieSubscriptions },
      { path: 'torrents', redirectTo: APP_ROUTE_SEGMENTS.torrentSearch, pathMatch: 'full' },
      { path: 'torrents/:value', redirectTo: 'search/torrents/:value' },
      { path: 'keywords', redirectTo: APP_ROUTE_SEGMENTS.movieSearch, pathMatch: 'full' },
      { path: 'keywords/:value', redirectTo: 'search/movies/:value' },
      { path: 'download', redirectTo: APP_ROUTE_SEGMENTS.downloads },
      { path: 'performer/:name', redirectTo: APP_ROUTE_SEGMENTS.performerDetail },
      { path: 'production/fc2/:id', redirectTo: APP_ROUTE_SEGMENTS.fc2MovieDetail },
      { path: 'production/:id', redirectTo: APP_ROUTE_SEGMENTS.movieDetail },
    ],
  },
  { path: APP_ROUTE_SEGMENTS.login, component: LoginComponent },
  { path: '**', redirectTo: APP_ROUTE_SEGMENTS.dashboard },
];
