import { Component, OnInit } from '@angular/core';
import { SettingsService } from './pages/services/settings.service';
import { GetTracksService } from './pages/services/get-tracks.service';

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

    this.settingsService.getSettings()
    .subscribe(
      (settings: any) => {
        this.settings = settings;
        console.log(this.settings);
        this.roomName = settings.roomName
      }
    )
  }
}
