import { CommonService } from './../../../../common.service';
import { Component, ElementRef, HostListener, inject } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { Location } from '@angular/common';
import { HomeService } from '../../service/home.service';
import { MatDialog } from '@angular/material/dialog';
import { SearchOptionComponent } from '../search-option/search-option.component';
import { ThemeService } from '../../../../theme.service';
import { CommonModule } from '@angular/common';
import { TranslateService } from '@ngx-translate/core';
@Component({
  selector: 'app-topbar',
  standalone: true,
  imports: [MatToolbarModule, MatIconModule, MatSidenavModule,CommonModule],
  templateUrl: './topbar.component.html',
  styleUrl: './topbar.component.css',
})
export class TopbarComponent {
  dialog: MatDialog = inject(MatDialog);
  langMenuOpen = false;

  constructor(
    private location: Location,
    public homeService: HomeService,
    public themeService: ThemeService,
    public commonService: CommonService,
    public translate: TranslateService,
    private elRef: ElementRef
  ) {}

  get currentLang(): string {
    return this.translate.currentLang || localStorage.getItem('appLang') || 'en';
  }

  toggleLangMenu() {
    this.langMenuOpen = !this.langMenuOpen;
  }

  closeLangMenu() {
    this.langMenuOpen = false;
  }

  setLanguage(lang: string) {
    this.translate.use(lang);
    localStorage.setItem('appLang', lang);
    this.langMenuOpen = false;
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    if (!this.elRef.nativeElement.querySelector('.lang-dropdown-wrapper')?.contains(event.target as Node)) {
      this.langMenuOpen = false;
    }
  }

  toggleSidebar() {
    this.homeService.setSidebarOpen(!this.homeService.isSidebarOpen);
  }
  OpenSearch() {
    const dialogRef = this.dialog.open(SearchOptionComponent, {});
  }
  goBack() {
    this.location.back();
  }
}
