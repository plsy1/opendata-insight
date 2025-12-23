import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DownloadStatisticComponent } from './download-statistic.component';

describe('DownloadStatisticComponent', () => {
  let component: DownloadStatisticComponent;
  let fixture: ComponentFixture<DownloadStatisticComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DownloadStatisticComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DownloadStatisticComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
