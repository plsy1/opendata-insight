import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { BackgroundTasksComponent } from './components/background-tasks/background-tasks.component';
import { ChangePasswordComponent } from './components/change-password/change-password.component';
import { EnvironmentVariableComponent } from './components/environment-variable/environment-variable.component';
import { SubscriptionRulesComponent } from './components/subscription-rules/subscription-rules.component';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [
    BackgroundTasksComponent,
    ChangePasswordComponent,
    CommonModule,
    EnvironmentVariableComponent,
    MatTabsModule,
    SubscriptionRulesComponent,
    TranslateModule,
  ],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.css',
})
export class SettingsComponent {
  selectedTabIndex = 0;
  currentLang: string;

  constructor(private translate: TranslateService) {
    this.currentLang =
      localStorage.getItem('appLang') ||
      this.translate.currentLang ||
      this.translate.getDefaultLang() ||
      'zh';
  }

  ngOnInit() {
    const savedIndex = sessionStorage.getItem('settingsTabIndex');
    if (savedIndex !== null) {
      this.selectedTabIndex = +savedIndex;
    }
  }

  onTabChange(event: any) {
    sessionStorage.setItem('settingsTabIndex', event.index);
  }

  changeLanguage(lang: string) {
    this.translate.use(lang);
    this.currentLang = lang;
    localStorage.setItem('appLang', lang);
  }
}
