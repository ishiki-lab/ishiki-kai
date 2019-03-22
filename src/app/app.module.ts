import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { HttpClientModule } from '@angular/common/http';
import { TrackSelectorComponent } from './pages/track-selector/track-selector.component';
import { TrackComponent } from './pages/track-selector/components/track/track.component';

import {AppRoutingModule } from './app-routing.module';
import { SplashScreenComponent } from './pages/splash-screen/splash-screen.component';
import { TrackControlComponent } from './pages/track-control/track-control.component';

import { CleanPathPipe } from './pages/pipes/clean-path.pipe';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

// material
import {
  MatButtonModule,
  MatIconModule,
  MatProgressSpinnerModule
} from '@angular/material';

@NgModule({
  declarations: [
    AppComponent,
    TrackSelectorComponent,
    TrackComponent,
    SplashScreenComponent,
    TrackControlComponent,
    CleanPathPipe
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    AppRoutingModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    BrowserAnimationsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
