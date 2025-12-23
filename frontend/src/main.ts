import { bootstrapApplication } from '@angular/platform-browser';
import { importProvidersFrom } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';

import { NgxEchartsModule } from 'ngx-echarts';

import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';

appConfig.providers = [
  ...(appConfig.providers || []),

  provideHttpClient(),

  importProvidersFrom(
    NgxEchartsModule.forRoot({
      echarts: () => import('echarts'),
    })
  ),
];

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));