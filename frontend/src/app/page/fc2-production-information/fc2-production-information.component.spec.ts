import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Fc2ProductionInformationComponent } from './fc2-production-information.component';

describe('Fc2ProductionInformationComponent', () => {
  let component: Fc2ProductionInformationComponent;
  let fixture: ComponentFixture<Fc2ProductionInformationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Fc2ProductionInformationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Fc2ProductionInformationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
