# Ishiki Kai

The new home for LushRooms and whatever it grows up to be

## Monorepo building

```sh
## player
git remote add player git@github.com:LUSHDigital/lrpi_player.git
git fetch player
# defacto latest commit on LUSHDigital/lrpi_player::master
git subtree add --prefix=player player rpi3_32bit_omxplayer


## tablet ui
git remote add tablet_ui git@github.com:InBrewJ/lrpi_tablet_ui.git
git fetch tablet_ui
git subtree add --prefix=tablet_ui tablet_ui jb/noodle/rpi3_pairing_fixes

## scentroom
git remote add scentroom git@github.com:LUSHDigital/lrpi_scentroom.git
git fetch scentroom
git subtree add --prefix=scentroom scentroom develop

##
```
