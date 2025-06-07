import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JobMatcherComponent } from './job-matcher.component';

describe('JobMatcherComponent', () => {
  let component: JobMatcherComponent;
  let fixture: ComponentFixture<JobMatcherComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [JobMatcherComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(JobMatcherComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
