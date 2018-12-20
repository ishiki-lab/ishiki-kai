import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class GetTracksService {

  // hostname: string = 'black-pearl.local';
  hostname: string = window.location.hostname;
  testnum: number = 0;
  playlist: any = null;

  constructor(
    private httpClient: HttpClient
  ) { }

  incT() {
    this.testnum++;
    console.log(this.testnum);
  }

  setPlaylist(data) {
    this.playlist = data;
  }

  getPlaylist() {
    return this.playlist;
  }

  getTracks(id) {
    let idQuery: string = '';

    if (id) {
      idQuery = '?id=' + id;
    }

    return this.httpClient.get('http://' + this.hostname + '/get-track-list' + idQuery);
  }

  scrubForward() {
    return this.httpClient.get('http://' + this.hostname + '/scrub-forward');
  }

  getSingleTrack(id) {
    return this.httpClient.get('http://' + this.hostname + '/get-single-track?id=' + id);
  }

  playSingleTrack(id) {
    return this.httpClient.get('http://' + this.hostname + '/play-single-track?id=' + id);
  }

  pauseSingleTrack(id) {
    return this.httpClient.get('http://' + this.hostname + '/pause-track?id=' + id);
  }

  stopMusic() {
    return this.httpClient.get('http://' + this.hostname + '/stop');
  }
}