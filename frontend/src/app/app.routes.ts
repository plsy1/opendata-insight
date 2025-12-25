import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { HomeComponent } from './page/home/home.component';
import { DashboardComponent } from './page/dashboard/dashboard.component';
import { SettingsComponent } from './page/settings/settings.component';
import { PerformerSubscriptionComponent } from './page/performer-subscription/performer-subscription.component';
import { ProductionSubscriptionComponent } from './page/production-subscription/production-subscription.component';
import { TorrentListComponent } from './page/torrent-list/torrent-list.component';
import { LoginComponent } from './page/login/login.component';
import { ExploreComponent } from './page/explore/explore.component';
import { DownloadComponent } from './page/download/download.component';
import { KeywordsSearchComponent } from './page/keywords-search/keywords-search.component';
import { PerformerInformationComponent } from './page/performer-information/performer-information.component';
import { ProductionInformationComponent } from './page/production-information/production-information.component';
import { Fc2ProductionInformationComponent } from './page/fc2-production-information/fc2-production-information.component';

export const routes: Routes = [
  {
    path: '',
    component: HomeComponent,
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        component: DashboardComponent,
        canActivate: [authGuard],
      },
      {
        path: 'settings',
        component: SettingsComponent,
        canActivate: [authGuard],
      },
      {
        path: 'explore',
        component: ExploreComponent,
        canActivate: [authGuard],
      },
      {
        path: 'subscription/performer',
        component: PerformerSubscriptionComponent,
        canActivate: [authGuard],
      },
      {
        path: 'subscription/production',
        component: ProductionSubscriptionComponent,
        canActivate: [authGuard],
      },
      {
        path: 'torrents',
        component: TorrentListComponent,
        canActivate: [authGuard],
      },
      {
        path: 'torrents/:value',
        component: TorrentListComponent,
        canActivate: [authGuard],
      },
      {
        path: 'download',
        component: DownloadComponent,
        canActivate: [authGuard],
      },
      {
        path: 'keywords',
        component: KeywordsSearchComponent,
        canActivate: [authGuard],
      },
      {
        path: 'keywords/:value',
        component: KeywordsSearchComponent,
        canActivate: [authGuard],
      },
      {
        path: 'performer/:name',
        component: PerformerInformationComponent,
        canActivate: [authGuard],
      },
      {
        path: 'production/:id',
        component: ProductionInformationComponent,
        canActivate: [authGuard],
      },
      {
        path: 'production/fc2/:id',
        component: Fc2ProductionInformationComponent,
        canActivate: [authGuard],
      },
    ],
  },
  { path: 'login', component: LoginComponent },
  { path: '**', redirectTo: '', canActivate: [authGuard] },
];
