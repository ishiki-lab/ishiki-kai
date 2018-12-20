import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import {Location} from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import {Router} from '@angular/router';
import { GetTracksService } from '../services/get-tracks.service';
import { of, Observable} from 'rxjs';
import { GetStylesService } from '../services/get-styles.service';
import { interval } from 'rxjs';
import { map } from 'rxjs/operators'

@Component({
  selector: 'app-track-control',
  templateUrl: './track-control.component.html',
  styleUrls: ['./track-control.component.css'],
  // encapsulation: ViewEncapsulation.ShadowDom
})
export class TrackControlComponent implements OnInit {
  serverData: Observable<any>;
  errorResponse = '';
  id: string;
  private sub: any;
  playing = false;
  duration = 'XX:XX:XX'
  now = '00:00:00'
  totalTicks: any = 0;
  ticks: number = 0;
  i_progress: number = 0;

  playlist: any = null;
  numTracks: number = 0;
  currentTrack: any = null;
  hrId: number = 0;

  constructor(
    private route: ActivatedRoute,
    private getTracksService: GetTracksService,
    private getStylesService: GetStylesService,
    private _location: Location,
    private router: Router
  ) {}

  pad(num): string {
    return ("0"+num).slice(-2);
  }

  hhmmss(secs): string {
    secs = Math.floor(secs);
    var minutes = Math.floor(secs / 60);
    secs = secs%60;
    var hours = Math.floor(minutes/60)
    minutes = minutes%60;
    return `${this.pad(hours)}:${this.pad(minutes)}:${this.pad(secs)}`;
  }

  isPlaying() {
    return this.playing && this.ticks < this.totalTicks;
  }

  next() {
    this.hrId = ((++this.hrId) % (this.numTracks));
    this.currentTrack = this.playlist[this.hrId];
  }

  previous() {
    this.hrId = ((--this.hrId) % (this.numTracks));
    this.currentTrack = this.playlist[this.hrId];
  }

  styleObject() {
    if (!this.getStylesService.getStyles()) {
      return {
        background: 'black',
      };
    }
  }

  styleObjectBorder() {
    if (!this.getStylesService.getStyles()) {
      return {
        border: 'none'
      };
    }
  }
  
  ngOnInit() {
    setInterval(() => { 
      if (this.playing && (this.ticks < +this.totalTicks)) {
        console.log('tick...');
        this.now = this.hhmmss(this.ticks += 1); 
      } else if (this.ticks >= +this.totalTicks && this.ticks != 0 && this.playing) {
        this.now = '00:00:00' 
        this.ticks = 0; 
        this.playing = false;
      }
      this.i_progress = Math.floor((this.ticks/this.totalTicks)*100)
    }, 1000);

    this.sub = this.route.params.subscribe(params => {
      this.id = params['id'];
    });

    this.playlist = this.getTracksService.getPlaylist();
    this.numTracks = this.playlist.length;
    this.currentTrack = this.playlist[0];

    this.getTracksService.getSingleTrack(this.id).subscribe(
      (data: any) => {
        console.log('from single track service: ', data);
        this.serverData = of(data);
      },
      (err: any) => {
        console.log('error', err);
        this.errorResponse = err;
        this.router.navigate([`/tracks`]);
      }
    );
  }

  playMusic() {
    this.playing = !this.playing;
    this.getTracksService.playSingleTrack(this.currentTrack.ID).subscribe(data => {
      this.duration = this.hhmmss(data)
      this.totalTicks = Math.floor(+data);
      console.log(data);
    });
  }

  pauseMusic() {
    this.playing = !this.playing;
    console.log(this.playing);
    this.getTracksService.pauseSingleTrack(this.currentTrack.ID).subscribe(data => {
      console.log(data);
    });
  }

  stopMusic() {
    this.getTracksService.stopMusic().subscribe(data => {
      console.log(data);
    });
    this.playing = false;
  }

  scrubForward() {
    this.getTracksService.scrubForward().subscribe(data => {
      this.now = this.hhmmss(data)
      this.ticks = +data;
      console.log(data);
    });
  }
}
