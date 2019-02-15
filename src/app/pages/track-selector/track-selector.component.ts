import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { of, Observable } from 'rxjs';
import { GetTracksService } from '../services/get-tracks.service';
import { GetStylesService } from '../services/get-styles.service';
import { ActivatedRoute } from '@angular/router';
import { Router } from '@angular/router';
import { SettingsService } from '../services/settings.service';
import { switchMap, map, mergeMap } from 'rxjs/operators';


@Component({
  selector: 'app-track-selector',
  templateUrl: './track-selector.component.html',
  styleUrls: ['./track-selector.component.css']
})
export class TrackSelectorComponent implements OnInit {
  title = 'mw_serve';
  serverData: Observable<any>;
  errorResponse: any = {};
  folderId = null;
  settings: any;
  roomName: string = '?';

  constructor(
    private httpClient: HttpClient,
    private getTracksService: GetTracksService,
    private getStylesService: GetStylesService,
    private settingsService: SettingsService,
    private route: ActivatedRoute,
    private router: Router
  ) {
  }


  styleObject() {
    if (!this.getStylesService.getStyles()) {
      return {
        border: 'none',
        paddingTop: '1.6rem'
      };
    }
  }

  itemStyleObject() {
    if (!this.getStylesService.getStyles()) {
      return {
        background: 'black',
        marginTop: '0.4em',
        marginBottom: '0.4em'
      };
    }
  }

  ngOnInit() {

    this.folderId = this.route.snapshot.queryParamMap.get("id");

    this.getTracksService.getStatus().pipe(
      switchMap((status: any) => {
        console.log('status in switchMap: ', status);
        if ( !(status.canControl || status.playerState || status.source) ) {
          console.log('player is idle, getting tracks...');
          return this.getTracksService.getTracks(this.folderId)
        } else {
          console.log('Player is active, updating this page...');
          this.getTracksService.setPlaylist(status.playlist);
          // update the shared service with the status to pass to the track controller
          this.getTracksService.setStatus(status);
          this.router.navigate([`/player`], { relativeTo: this.route, skipLocationChange: true });
          
          return of(status);
        }
      })
    ).subscribe(
      (d: any) => {
        console.log('In the playlist processor');
        
        let data: any = d;

        console.log('tracks: ', data, ' length: ', data.length);

        let dataLen = data.length;
        let isPlaylist: boolean = true;

        if (data.length === undefined) {
          this.errorResponse['message'] = 'Syncing may not have completed yet. Alternatively, is the usb stick plugged in?'
          this.serverData = null;
          return;
        }

        if (data.playlist) {
          data = data.playlist;
          dataLen = data.length;
        }

        console.log('playlist: ', data);

        for (let i = 0; i < dataLen; i++) {
          if (data[i].IsDir === true) {
            isPlaylist = false;
            break;
          }
        }

        if (isPlaylist) {
          this.getTracksService.setPlaylist(data);
          this.router.navigate([`/player`], { relativeTo: this.route, skipLocationChange: true });
        }

        console.log('playlist? : ', isPlaylist);

        this.serverData = of(
          data
        );

      },
      (err: any) => {
        console.log('error', err);
        this.errorResponse = err;
        this.errorResponse['message'] = 'Something is wrong...'
        this.router.navigate([`/tracks`]);
      }
    )

  }
}
