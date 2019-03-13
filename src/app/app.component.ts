import { Component, OnInit } from '@angular/core';
import { SettingsService } from './pages/services/settings.service';
import { GetTracksService } from './pages/services/get-tracks.service';
import { forkJoin } from 'rxjs';
import { PairingService } from './pages/services/pairing.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'mw_serve';
  settings: any;
  roomName: string = '?';
  canPair: boolean = false;
  partyModeActive: boolean = false;
  slaveIp: string
  slaved: boolean = false;


  constructor(
    private settingsService: SettingsService,
    private tracksService: GetTracksService,
    private pairingService: PairingService
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
        // this.tracksService.setStatus(status);
        // console.log('ac: ', this.tracksService.getInternalStatus())
        console.log('settings: ', settings);
        this.slaveIp = settings.slave_ip;
        this.settings = settings;
        // console.log(this.settings);
        this.roomName = settings.roomName
        // this.slaveIp = settings.
        if (settings.paired && settings.slaveIp == "") {
          this.slaved = true;
        }
      }
    );
  }

  pair() {
    this.pairingService.pair(this.slaveIp).subscribe(
      (res: any) => {
        console.log('Pair res: ', res);
        if(res === 0) {
          this.partyModeActive = true;
        }
      }
    )
  }

  unpair() {
    console.log('Unpair has not yet been written...');
  }
}
