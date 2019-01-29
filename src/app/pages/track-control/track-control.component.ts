import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import {Location} from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import {Router} from '@angular/router';
import { GetTracksService } from '../services/get-tracks.service';
import { of, Observable} from 'rxjs';
import { GetStylesService } from '../services/get-styles.service';
import { interval } from 'rxjs';
import { map } from 'rxjs/operators';
import {
  trigger,
  state,
  style,
  animate,
  transition,
  // ...
} from '@angular/animations';

@Component({
  selector: 'app-track-control',
  templateUrl: './track-control.component.html',
  styleUrls: ['./track-control.component.css'],
  animations: [
    // the fade-in/fade-out animation.
    trigger('simpleFadeAnimation', [

      // the "in" style determines the "resting" state of the element when it is visible.
      state('in', style({opacity: 1})),
      state('out', style({opacity: 0})),

      transition('out => in', [
        animate('0.4s')
      ]),
      transition('in => out', [
        animate('4s')
      ]),
    ])
  ]
})
export class TrackControlComponent implements OnInit {
  serverData: Observable<any>;
  errorResponse = '';
  id: string;
  private sub: any;
  started = false;
  playing = false;
  skipped = false;
  loading = false;
  crossfading = false;
  duration = 'XX:XX:XX';
  now = '00:00:00';
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

  isWaiting() {
    return (this.playing && this.duration === 'XX:XX:XX') ||
           (!this.playing && this.ticks > 0 && this.skipped);
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
        this.now = this.hhmmss(this.ticks += 1); 
      } else if (this.ticks >= +this.totalTicks && this.ticks != 0 && this.playing) {
        this.now = '00:00:00' 
        this.ticks = 0; 
        // Play the next track in the playlist
        // automatically
        this.playing = false;
        this.skipped = false;
        this.duration = 'XX:XX:XX';
        // TODO: needs to loop on LOOP tracks?
        // Skip only on command
        this.next(undefined);
      }
      this.i_progress = Math.floor((this.ticks/this.totalTicks)*100)
    }, 1000);

    this.sub = this.route.params.subscribe(params => {
      this.id = params['id'];
    });

    this.playlist = this.getTracksService.getPlaylist();
    this.numTracks = this.playlist.length;
    this.currentTrack = this.playlist[0];

  }

  play() {
    this.loading = true;
    if (!this.started) {
      this.getTracksService.playSingleTrack(this.currentTrack.ID).subscribe(data => {
        this.loading = false;
        this.duration = this.hhmmss(data)
        this.started = true;
        this.playing = true;
        this.totalTicks = Math.floor(+data);
        console.log(data);
      });
    } else {
      this.getTracksService.playPause().subscribe(data => {
        this.loading = false;
        this.playing = true;
        this.duration = this.hhmmss(data)
        console.log(data);
      });  
    }
  }

  pause() {
    this.playing = false;
    this.getTracksService.playPause().subscribe(data => {
      this.duration = this.hhmmss(data)
      console.log(data);
    });
  }

  next(interval) {
    if(!this.loading) {
      this.hrId = ((++this.hrId) % (this.numTracks));
      this.fadeToTrack(
        this.hrId, 
        this.playing ? interval : 0
      );
    }
  }

  previous(interval) {
    if(!this.loading) {
      if (this.hrId > 0) {
        this.hrId = ((--this.hrId) % (this.numTracks));
        this.currentTrack = this.playlist[this.hrId];
        this.fadeToTrack(
          this.hrId, 
          this.playing ? interval : 0
        );
      }
    }
  }

  fadeToTrack(id, interval) {
    // if we're not playing a track, we're just scrolling through, but if a track is playing we need to fade to a track
    if (
        this.playing || this.started || 
        (interval === 0 && this.duration === 'XX:XX:XX' && this.started)
      ) {
      this.crossfading = true;
      this.loading = true
      this.skipped = true;
      this.playing = false;
      this.getTracksService.crossfade(
        this.playlist[id].ID,
        interval
      ).subscribe(data => {
        if (data > 0) {
          this.loading = false
          this.playing = true
          this.ticks = 0;
          this.duration = this.hhmmss(data)
          this.currentTrack = this.playlist[id];
          this.totalTicks = Math.floor(+data);
          this.skipped = false;
          this.crossfading = false;
          console.log(data);
        } else {
          console.log('ERROR ON CROSSFADE!');
        }
        
      });  
    } else {
      this.currentTrack = this.playlist[id];
    }

  }

  getClickedProgressBarPercentage(a, b, barWidth) {
    return Math.floor(( (a + b) / barWidth ) * 100.0);
  }

  // Only seek if we have an mp4 on our hands, MLPs will break everything
  trackIsMp4() {
    let filename = this.currentTrack.Name;
    return filename.substring(filename.lastIndexOf('.')+1, filename.length) === 'mp4';
  }

  tapToSeek(e, direction) {
    if (this.started && this.trackIsMp4()) {

      let progressBarWidth = document.getElementById('progress-bar').offsetWidth;
      let clickedBarWidth = e.srcElement.offsetWidth;

      let a = progressBarWidth - clickedBarWidth;
      let b = clickedBarWidth * 
      (e.offsetX/e.srcElement.offsetWidth);
      let progressAlongFullBar = 50.0; // go to the middle of the track if something goes wrong

      if (direction === 'f') {
        progressAlongFullBar = this.getClickedProgressBarPercentage(a, b, progressBarWidth);  
      } else if (direction === 'b') {
        progressAlongFullBar = this.getClickedProgressBarPercentage(b, 0, progressBarWidth);
      }

      if (progressAlongFullBar === 100) {
        // Don't seek right to the end, omxplayer will fall over
        progressAlongFullBar = 98.0
      }

      this.getTracksService.tapToSeek(progressAlongFullBar).subscribe(data => {
        this.now = this.hhmmss(data)
        this.ticks = +data;
      });
    }
  }

  stop() {
    this.getTracksService.stopMusic().subscribe(data => {
      console.log(data);
    });
    this.playing = false;
  }

}