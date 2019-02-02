import { Component, OnInit } from '@angular/core';
import { SettingsService } from './pages/services/settings.service';
import { GetTracksService } from './pages/services/get-tracks.service';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'mw_serve';
  settings: any;
  roomName: string = '?';


  constructor(
    private settingsService: SettingsService,
    private tracksService: GetTracksService
  ) {
  }

  ngOnInit () {


    forkJoin(
      this.tracksService.getStatus(),
      this.settingsService.getSettings()
    ).subscribe(
      ([statusRes, settingsRes]) => {
        let settings: any = settingsRes;
        let status: any = statusRes
        this.tracksService.setStatus(status);
        // console.log('ac: ', this.tracksService.getInternalStatus())
        this.settings = settings;
        // console.log(this.settings);
        this.roomName = settings.roomName
      }
    );
  }
}
