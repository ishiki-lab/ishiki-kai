# Ishiki Kai

The new home for LushRooms and whatever it grows up to be

## Monorepo building

```sh

git remote add player git@github.com:LUSHDigital/lrpi_player.git
git fetch player
# defacto latest commit on LUSHDigital/lrpi_player::master
git subtree add --prefix=player player rpi3_32bit_omxplayer

```
