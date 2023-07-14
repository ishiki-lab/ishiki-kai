import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { TrackSelectorComponent } from "./pages/track-selector/track-selector.component";
import { SplashScreenComponent } from "./pages/splash-screen/splash-screen.component";
import { TrackControlComponent } from "./pages/track-control/track-control.component";

const routes: Routes = [
  {
    path: "",
    redirectTo: "/tracks",
    pathMatch: "full",
  },
  {
    path: "splash",
    component: SplashScreenComponent,
  },
  {
    path: "tracks",
    component: TrackSelectorComponent,
  },
  {
    path: "player",
    component: TrackControlComponent,
  },
];

const DEBUG_ROUTE_TRACING: boolean = false;

@NgModule({
  imports: [
    RouterModule.forRoot(routes, { enableTracing: DEBUG_ROUTE_TRACING }),
  ],
  exports: [RouterModule],
})
export class AppRoutingModule {}
