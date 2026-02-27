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
    this.translate.addLangs(['en', 'zh']);
    this.translate.setDefaultLang('en');
    
    const savedLang = localStorage.getItem('appLang');
    if (savedLang && savedLang.match(/en|zh/)) {
      this.translate.use(savedLang);
    } else {
      // Use the browser language, or default to English
      const browserLang = this.translate.getBrowserLang();
      this.translate.use(browserLang?.match(/en|zh/) ? browserLang : 'en');
    }
  }
}
