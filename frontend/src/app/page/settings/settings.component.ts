import { Component } from '@angular/core';
import { EnvironmentVariableComponent } from "./components/environment-variable/environment-variable.component";
import { ChangePasswordComponent } from "./components/change-password/change-password.component";
import { BackgroundTasksComponent } from './components/background-tasks/background-tasks.component';
import { MatTabsModule } from '@angular/material/tabs';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [EnvironmentVariableComponent, ChangePasswordComponent, BackgroundTasksComponent, MatTabsModule, TranslateModule, CommonModule],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.css'
})
export class SettingsComponent {

  selectedTabIndex = 0;
  currentLang: string;

  constructor(private translate: TranslateService) {
    this.currentLang = localStorage.getItem('appLang') || this.translate.currentLang || this.translate.getDefaultLang() || 'zh';
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

