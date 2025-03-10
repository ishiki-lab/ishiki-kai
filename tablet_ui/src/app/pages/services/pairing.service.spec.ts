import { TestBed, inject } from '@angular/core/testing';

import { PairingService } from './pairing.service';

describe('PairingService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [PairingService]
    });
  });

  it('should be created', inject([PairingService], (service: PairingService) => {
    expect(service).toBeTruthy();
  }));
});
