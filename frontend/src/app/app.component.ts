import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { CommonService } from './common.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  title = 'test';

  constructor(
    private translate: TranslateService,
    private commonService: CommonService,
    private snackBar: MatSnackBar
  ) {
    this.translate.addLangs(['en', 'zh', 'ja']);
    this.translate.setDefaultLang('en');
    
    const savedLang = localStorage.getItem('appLang');
    if (savedLang && savedLang.match(/en|zh|ja/)) {
      this.translate.use(savedLang);
    } else {
      // Auto-detect from browser, persist the result
      const browserLang = this.translate.getBrowserLang();
      const detectedLang = browserLang?.match(/en|zh|ja/) ? browserLang : 'en';
      this.translate.use(detectedLang);
      localStorage.setItem('appLang', detectedLang);
    }
  }

  ngOnInit() {
    this.checkUpdate();
  }

  checkUpdate() {
    forkJoin({
      current: this.commonService.getSystemVersion(),
      latest: this.commonService.checkUpdate()
    }).subscribe({
      next: ({ current, latest }) => {
        if (latest.latest_version && current.version !== latest.latest_version) {
          this.commonService.setHasUpdate(true);
        }
      },
      error: (err) => {
        console.error('Failed to check for updates:', err);
      }
    });
  }
}
