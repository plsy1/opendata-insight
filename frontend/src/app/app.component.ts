import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'test';

  constructor(private translate: TranslateService) {
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
}
