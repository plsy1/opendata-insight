// src/app/theme.service.ts
import { Injectable, OnDestroy } from '@angular/core';
export type ThemeMode = 'light' | 'dark' | 'system';

@Injectable({ providedIn: 'root' })
export class ThemeService implements OnDestroy {
  private currentTheme: ThemeMode;
  private mediaQueryList = window.matchMedia('(prefers-color-scheme: dark)');
  private listener = () => {
    if (this.currentTheme === 'system') {
      this.applyTheme('system');
    }
  };

  constructor() {
    const saved = localStorage.getItem('themeMode') as ThemeMode | null;
    this.currentTheme = saved || 'system';
    this.applyTheme(this.currentTheme);
    this.mediaQueryList.addEventListener('change', this.listener);
  }

  ngOnDestroy() {
    this.mediaQueryList.removeEventListener('change', this.listener);
  }

  isDarkTheme(): boolean {
    if (this.currentTheme === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return this.currentTheme === 'dark';
  }

  getThemeIcon(): string {
    switch (this.currentTheme) {
      case 'light':
        return 'fa-sun';
      case 'dark':
        return 'fa-moon';
      case 'system':
        return 'fa-desktop';
    }
  }

  toggleTheme() {
    switch (this.currentTheme) {
      case 'light':
        this.currentTheme = 'dark';
        break;
      case 'dark':
        this.currentTheme = 'system';
        break;
      case 'system':
        this.currentTheme = 'light';
        break;
    }
    localStorage.setItem('themeMode', this.currentTheme);
    this.applyTheme(this.currentTheme);
  }

  private setMetaThemeColor(color: string) {
    let meta = document.querySelector('meta[name="theme-color"]');
    if (!meta) {
      meta = document.createElement('meta');
      meta.setAttribute('name', 'theme-color');
      document.head.appendChild(meta);
    }
    meta.setAttribute('content', color);
  }

  private applyTheme(mode: ThemeMode) {
    const body = document.body;
    body.classList.remove('light-theme', 'dark-theme');

    let themeColor = '#f1f5f9';
    if (mode === 'light') {
      body.classList.add('light-theme');
      themeColor = '#f1f5f9';
    } else if (mode === 'dark') {
      body.classList.add('dark-theme');
      themeColor = '#09090b';
    } else {
      if (this.mediaQueryList.matches) {
        body.classList.add('dark-theme');
        themeColor = '#09090b';
      } else {
        body.classList.add('light-theme');
        themeColor = '#f1f5f9';
      }
    }

    this.setMetaThemeColor(themeColor);
  }
}
