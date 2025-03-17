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

## scentroom ui
git remote add scentroom_ui git@github.com:LUSHDigital/lrpi_scentroom_ui.git
git fetch scentroom_ui
git subtree add --prefix=scentroom_ui scentroom_ui reboot_button

# Lush source at:
# https://github.com/orgs/LUSHDigital/repositories?language=&q=lrpi&sort=&type=all
## be wary of forks on inbrewj / pisuke / ishiki-lab
#
# TO ADD
## lrpi_record

git remote add record git@github.com:LUSHDigital/lrpi_record.git
git fetch record
git subtree add --prefix=record record master

## lrpi_bootstrap
### note: how does this overlap with ishiki-bootstrap?
### see here for the cerbot / TLS setup: https://github.com/InBrewJ/lrpi_bootstrap/tree/portainer_instance_nginx_with_tls_certbot
#
### As far as I can tell for now, ishiki-bootstrap doesn't have Portainer
### run / operate config

git remote add bootstrap git@github.com:InBrewJ/lrpi_bootstrap.git
git fetch bootstrap
git subtree add --prefix=bootstrap bootstrap portainer_instance_nginx_with_tls_certbot

## lrpi_display

## lrpi_ap

## lrpi_rclone

# SS'd (or might be?)
## lrpi_brickd (-> ishiki-brickd ??)
## lrpi_base (-> ishiki-base ??)

```
