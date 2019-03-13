import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PairingService {

  hostname: string = environment.hostname;

  constructor(
    private httpClient: HttpClient
  ) { }

  pair(pairhostname: string) {
    let pairQuery: string = '';

    if (pairhostname) {
      pairQuery = '?pairhostname=' + pairhostname;
    }

    return this.httpClient.get('http://' + this.hostname + '/pair' + pairQuery);
  }

  unpair() {
    return this.httpClient.get('http://' + this.hostname + '/unpair');
  }

}
