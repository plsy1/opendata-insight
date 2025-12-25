import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Fc2Component } from './fc2.component';

describe('Fc2Component', () => {
  let component: Fc2Component;
  let fixture: ComponentFixture<Fc2Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Fc2Component]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Fc2Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
