import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, Router } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { MatTabChangeEvent } from '@angular/material/tabs';

import { DashboardComponent } from './dashboard.component';

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;
  let router: jasmine.SpyObj<Router>;
  let queryParams: BehaviorSubject<ReturnType<typeof convertToParamMap>>;
  let route: {
    queryParamMap: BehaviorSubject<ReturnType<typeof convertToParamMap>>;
    snapshot: { queryParamMap: ReturnType<typeof convertToParamMap> };
  };

  beforeEach(async () => {
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    router.navigate.and.resolveTo(true);
    queryParams = new BehaviorSubject(convertToParamMap({ tab: 'statistics' }));
    route = {
      queryParamMap: queryParams,
      snapshot: { queryParamMap: convertToParamMap({ tab: 'statistics' }) },
    };

    await TestBed.configureTestingModule({
      imports: [DashboardComponent],
      providers: [
        { provide: ActivatedRoute, useValue: route },
        { provide: Router, useValue: router },
      ],
    })
    .overrideComponent(DashboardComponent, { set: { template: '' } })
    .compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('restores the statistics tab from the URL', () => {
    expect(component.selectedTabIndex).toBe(1);

    queryParams.next(convertToParamMap({}));

    expect(component.selectedTabIndex).toBe(0);
  });

  it('stores the selected tab in the current history entry', () => {
    route.snapshot.queryParamMap = convertToParamMap({});

    component.onTabChange({ index: 1 } as MatTabChangeEvent);

    expect(router.navigate).toHaveBeenCalledWith([], {
      relativeTo: route as unknown as ActivatedRoute,
      queryParams: { tab: 'statistics' },
      queryParamsHandling: 'merge',
      replaceUrl: true,
    });
  });
});
