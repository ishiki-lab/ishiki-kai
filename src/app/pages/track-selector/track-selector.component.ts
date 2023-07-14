import { Component, OnInit } from "@angular/core";
import { of, Observable } from "rxjs";
import { GetTracksService } from "../services/get-tracks.service";
import { GetStylesService } from "../services/get-styles.service";
import { ActivatedRoute } from "@angular/router";
import { Router } from "@angular/router";
import { switchMap } from "rxjs/operators";

@Component({
  selector: "app-track-selector",
  templateUrl: "./track-selector.component.html",
  styleUrls: ["./track-selector.component.css"],
})
export class TrackSelectorComponent implements OnInit {
  title = "mw_serve";
  serverData: Observable<any>;
  errorResponse: any = {};
  folderId = null;
  settings: any;
  roomName: string = "?";
  loading = true;

  constructor(
    private getTracksService: GetTracksService,
    private getStylesService: GetStylesService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    // This is a little bit React 12
    // "onComponentDidChange" vibes...
    let last_id = "";
    route.queryParams.subscribe(({ id }) => {
      console.log(`id param changed to :: ${id} from ${last_id}`);
      if (id !== last_id) {
        this.folderId = id;
        console.log("Attempting to pass to player...");
        this.getTracksService
          .getStatus()
          .pipe(switchMap(this.isPlayerReady))
          .subscribe(this.processPlaylist, this.handleErrors);
      }
      last_id = id;
    });
  }

  styleObject() {
    if (!this.getStylesService.getStyles()) {
      return {
        border: "none",
        paddingTop: "1.6rem",
      };
    }
  }

  itemStyleObject() {
    if (!this.getStylesService.getStyles()) {
      return {
        background: "black",
        marginTop: "0.4em",
        marginBottom: "0.4em",
      };
    }
  }

  processPlaylist = (_statusOrPlaylist: any) => {
    console.log("In the playlist processor");

    let statusOrPlaylist: any = _statusOrPlaylist;

    console.log(
      "statusOrPlaylist: ",
      statusOrPlaylist,
      " length: ",
      statusOrPlaylist.length
    );

    let dataLen = statusOrPlaylist.length;
    let isPlaylist: boolean = true;

    if (statusOrPlaylist.length === undefined) {
      this.errorResponse["message"] =
        "Syncing may not have completed yet. Alternatively, is the usb stick plugged in?";
      this.loading = false;
      this.serverData = null;
      return;
    }

    if (statusOrPlaylist.playlist) {
      statusOrPlaylist = statusOrPlaylist.playlist;
      dataLen = statusOrPlaylist.length;
    }

    console.log("playlist: ", statusOrPlaylist);

    for (let i = 0; i < dataLen; i++) {
      if (statusOrPlaylist[i].IsDir === true) {
        isPlaylist = false;
        break;
      }
    }

    if (isPlaylist) {
      this.getTracksService.setPlaylist(statusOrPlaylist);
      this.router.navigate([`/player`], {
        relativeTo: this.route,
        skipLocationChange: true,
      });
    }

    console.log("playlist? : ", isPlaylist);
    this.loading = false;

    this.serverData = of(statusOrPlaylist);
  };

  handleErrors = (err: any) => {
    console.log("error", err);
    this.errorResponse = err;
    this.loading = false;
    this.errorResponse["message"] =
      "Something is wrong. Please refresh and try again...";
    this.router.navigate([`/tracks`]);
  };

  isPlayerReady = (status: any) => {
    console.log("status from server: ", status);
    this.getTracksService.setStatus(status);

    // if we're trying to control a slaved 'Pi lock the UI

    const playerIsEnslaved = status.paired && status.master_ip;

    if (playerIsEnslaved) {
      this.serverData = null;
      this.errorResponse["message"] =
        "Currently paired to: " + status.master_ip + " -> controls are locked!";
      return of(status);
    }

    const cannotControlPlayer = status.canControl === false;

    if (cannotControlPlayer) {
      console.log("Player is not yet playing, calling get-track-list...");
      return this.getTracksService.getTracks(this.folderId);
    } else {
      this.getTracksService.setPlaylist(status.playlist);
      // update the shared service with the status to pass to the track controller
      this.getTracksService.setStatus(status);
      this.router.navigate([`/player`], {
        relativeTo: this.route,
        skipLocationChange: true,
      });

      return of(status);
    }
  };

  ngOnInit() {
    this.folderId = this.route.snapshot.queryParamMap.get("id");
    this.loading = true;

    // this.getTracksService
    //   .getStatus()
    //   .pipe(switchMap(this.isPlayerReady))
    //   .subscribe(this.processPlaylist, this.handleErrors);
  }

  navigateToPlaylist(trackOrFolderId: number) {
    console.log("Hack navigation to :: ", trackOrFolderId);

    this.router.navigate([`/tracks`], {
      relativeTo: this.route,
      queryParams: { id: trackOrFolderId },
      queryParamsHandling: "merge",
    });
  }
}
