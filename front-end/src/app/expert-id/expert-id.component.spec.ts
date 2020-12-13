import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExpertIdComponent } from './expert-id.component';

describe('ExpertIdComponent', () => {
  let component: ExpertIdComponent;
  let fixture: ComponentFixture<ExpertIdComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExpertIdComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExpertIdComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
