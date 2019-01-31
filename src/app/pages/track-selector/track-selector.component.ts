import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { of, Observable } from 'rxjs';
import { GetTracksService } from '../services/get-tracks.service';
import { GetStylesService } from '../services/get-styles.service';
import { ActivatedRoute  } from '@angular/router';
import {Router} from '@angular/router';
import { SettingsService } from '../services/settings.service';

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
      return{
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

  ngOnInit () {

    this.folderId = this.route.snapshot.queryParamMap.get("id");

    this.getTracksService.getTracks(this.folderId).subscribe(
      (data: any) => {
        console.log('tracks: ', data, ' length: ', data.length);

        let dataLen = data.length;
        let isPlaylist: boolean = true;

        if (data.length === undefined) {
          this.errorResponse['message'] = 'Is the usb stick plugged in?' 
          this.serverData = null;
          return;
        }

        for (let i = 0; i < dataLen; i++) {
          if (data[i].IsDir === true) {
            isPlaylist = false;
            break;
          }
        }

        if (isPlaylist) {
          this.getTracksService.setPlaylist(data);
          this.router.navigate([`/player`], {relativeTo: this.route, skipLocationChange: true});
        }

        console.log('playlist? : ', isPlaylist);
        
        this.serverData = of(
          data
        );
      },
      (err: any) => {
        console.log('error', err);
        this.errorResponse = err;
        this.router.navigate([`/tracks`]);
      }
    );
  }
}
