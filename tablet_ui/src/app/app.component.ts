import { Component, OnInit } from "@angular/core";
import { SettingsService } from "./pages/services/settings.service";
import { GetTracksService } from "./pages/services/get-tracks.service";
import { forkJoin } from "rxjs";
import { PairingService } from "./pages/services/pairing.service";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.css"],
})
export class AppComponent implements OnInit {
  title = "LushRoomsPi";
  settings: any;
  roomName: string = "?";
  canPair: boolean = false;
  partyModeActive: boolean = false;
  slaveIp: string;
  masterIp: string;
  slaved: boolean = false;
  pairingInProgress: boolean = false;
  unPairingInProgress: boolean = false;
  pairingError: boolean = false;

  constructor(
    private settingsService: SettingsService,
    private tracksService: GetTracksService,
    private pairingService: PairingService
  ) {}

  ngOnInit() {
    forkJoin(
      this.tracksService.getStatus(),
      this.settingsService.getSettings()
    ).subscribe(([statusRes, settingsRes]) => {
      // init the slave indicators
      this.slaved = false;
      this.masterIp = null;
      this.partyModeActive = false;

      let settings: any = settingsRes;
      let status: any = statusRes;
      // this.tracksService.setStatus(status);
      // console.log('ac: ', this.tracksService.getInternalStatus())
      console.log("settings: ", settings);
      this.slaveIp = settings.slave_ip;
      this.settings = settings;
      // console.log(this.settings);
      this.roomName = settings.roomName;
      // this.slaveIp = settings

      if (status.master_ip) {
        this.slaved = true;
        this.masterIp = status.master_ip;
      } else if (status.paired && settings.slaveIp != "") {
        this.partyModeActive = true;
      }
    });
  }

  pair() {
    this.pairingInProgress = true;
    this.pairingError = false;
    this.pairingService.pair(this.slaveIp).subscribe((res: any) => {
      console.log("Pair res: ", res);
      if (res === 0) {
        this.pairingInProgress = false;
        this.partyModeActive = true;
      }

      if (res === 1) {
        this.pairingInProgress = false;
        this.partyModeActive = false;
        this.pairingError = true;
      }
    });
  }

  unpair() {
    this.unPairingInProgress = true;
    this.pairingError = false;
    this.pairingService.unpair().subscribe((res: any) => {
      console.log("unpair res: ", res);
      if (res === 0) {
        this.unPairingInProgress = false;
        this.partyModeActive = false;
      }
    });
  }
}
