from crypt import crypt
from Crypto.PublicKey import RSA
from Crypto import Random
import uuid
import json
from fabric.api import local, settings, abort, run, env, sudo, put, get, prefix
from fabric.contrib.files import exists

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from config import (NEW_PASSWORD,
                    NEW_USERNAME,
                    NEW_HOSTNAME,
                    CHANGED_PASSWORD,
                    ROOT_PASSWORD,
                    ORIGINAL_HOSTNAME,
                    ORIGINAL_PASSWORD,
                    ORIGINAL_USERNAME,
                    ACCESS_IP,
                    CERTS_NAME
                    )

default_host = ACCESS_IP if ACCESS_IP is not None else "%s.local" % ORIGINAL_HOSTNAME
default_hosts = ["%s:%s" % (default_host, 22)]
renamed_hosts = ["%s.local:%s" % (NEW_HOSTNAME, 22)]

CERTS_DIR = os.path.abspath(os.path .join(os.path.dirname(__file__), "..", "certs"))
USB_DIR = os.path.abspath(os.path .join(os.path.dirname(__file__), "..", "usb"))

if not os.path.exists(CERTS_DIR):
    raise Exception("couldn't find certs")


def get_cert_path(private=False):
    if private:
        return os.path.join(CERTS_DIR, CERTS_NAME)
    else:
        return os.path.join(CERTS_DIR, "%s.pub" % CERTS_NAME)

env.hosts = default_host
env.user = NEW_USERNAME
# env.password = NEW_PASSWORD
env.key_filename = get_cert_path(private=True)

# Raspbian supporting KeDei touch screen
# http://www.kedei.net/raspberry/v6_1/rpi_35_v6_3_stretch_kernel_4_15_18.rar
# RASPBIAN_VERSION = "KeDei Raspbian rpi_v6_3_stretch_kernel_4_15_18"
# RASPBIAN_VERSION = "Raspbian rpi_v6_3_stretch_kernel_4_15_18"

RASPBIAN_VERSION = "2018-11-13-raspbian-stretch-lite"

############################################################################
##              Preparing the base disc image from JESSIE_VERSION
############################################################################

"""
    On local machine install requirements.txt with pip

    Set up the Raspberry Pi before creading a card can be done with raspi-config
    Login to Raspberry Pi as "pi" with password "raspberry"
    "sudo raspi-config"
    Network Options > Wi-fi <enter country, SSID & passphrase>
    Interfacing Options > SSH > Yes
    Finish
    Then check ip address with "ifconfig"
"""



###############################################################################################

def create_settings(number):

    public, private = newkeys(1024)
    private_key = private.exportKey('PEM').decode("utf-8")
    public_key = public.exportKey('OpenSSH').decode("utf-8")
    device_uuid = str(uuid.uuid4())

    settings = {
        "url": "https://lushroom.com/api/config/%s" % device_uuid,
        "public_key": "%s lushroom-%s@lushroom.com" % (public_key, number),
        "private_key": private_key,
        "uuid": device_uuid,
        "name": "lushroom-%s" % number,
        "description": "A Lushroom",
        "hue1_ip": "192.168.1.5",
        "hue2_ip": "192.168.1.6",
        "hue1_name": "room 1",
        "hue2_name": "room 2",
        "influx_host": "",
        "influx_port": "",
        "influx_dbname": "",
        "influx_ssl": "True",
        "influx_username": "",
        "influx_password": "",
        "time_zone": "Europe/London",
        "ssid": "",
        "psk": "",
        "host_name": "lushroom-%s" % number,
        "tunnel_host": "35.205.94.204",
        "tunnel_port": "%s" % (5000 + int(number)),
        "tunnel_user": "lushroom-%s" % number
    }

    usb_dir = os.path.join(USB_DIR, "lushroom-%s" % number)

    if not os.path.exists(usb_dir):
        os.makedirs(usb_dir)

    path = os.path.join(usb_dir, "settings.json")

    with open(path, "w") as f:
        f.write(json.dumps(settings, sort_keys=True, indent=4))


def prepare_card(config="default"):
    """
    Prepares the base image
    """

    # use the devices given login
    env.key_filename = None
    env.user = ORIGINAL_USERNAME
    env.password = ORIGINAL_PASSWORD

    # create a new user and change the passwords for the root and default users
    create_new_user()
    env.user = NEW_USERNAME
    env.password = NEW_PASSWORD
    change_default_password()
    copy_certs()
    set_ssh_config()
    env.password = None
    env.key_filename = get_cert_path(private=True)
    change_root_password()

    # add libs, drivers and tidy up

    install_pip()
    install_extra_libs()
    install_docker()
    reduce_writes()
    set_boot_config(config)
    remove_bloat()

    # add our bootstrap software
    add_bootstrap()

    set_hostname()

    print("*****************  After this run fab fix_install ********************")
    # this is crashing at end of install/opt
    waveshare_install_SPI_touchscreen_drivers()
    sudo("shutdown now")

def finish_prepare():
    fix_install()
    sudo("apt-get clean")
    sudo("python3 /opt/lushroom/clean_wifi.py")
    sudo("rm /opt/lushroom/clean_wifi.py")
    sudo("raspi-config --expand-rootfs")
    sudo("shutdown now")


def dev_setup():
    """
    prepares a base image
    """

    set_ssh_config_dev() # allows password login
    install_samba()
    install_dev_apt_prerequisites()
    install_dev_pip_prerequisites()
    create_lushroom_dev()

###############################################################################################



def list_usb():
    sudo('ls /media/usb/')

def newkeys(keysize):
    random_generator = Random.new().read
    key = RSA.generate(keysize, random_generator)
    private, public = key, key.publickey()
    return public, private

def create_new_user():
    # create user
    sudo("adduser %s" % NEW_USERNAME)
    # make sudo
    sudo("usermod -aG sudo %s" % NEW_USERNAME)
    crypted_password = crypt(NEW_PASSWORD, 'salt')
    sudo('usermod --password %s %s' % (crypted_password, NEW_USERNAME), pty=False)
    # sudo without password
    sudo('echo "%s%s ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers' % ("%", NEW_USERNAME))


def change_default_password():
    crypted_password = crypt(CHANGED_PASSWORD, 'salt')
    sudo('usermod --password %s %s' % (crypted_password, ORIGINAL_USERNAME), pty=False)


def copy_certs():
    run("mkdir /home/%s/.ssh" % NEW_USERNAME)
    run("chmod 700 /home/%s/.ssh" % NEW_USERNAME)
    cert_path = get_cert_path()
    put(cert_path, "/home/%s/.ssh/authorized_keys" % NEW_USERNAME)
    run("chmod 600 /home/%s/.ssh/authorized_keys" % NEW_USERNAME)


def set_ssh_config():
    env.key_filename = get_cert_path(private=True)
    _add_config_file("sshd_config", "/etc/ssh/sshd_config", "root", chmod="600")
    sudo("sudo systemctl restart ssh")


def set_ssh_config_dev():
    env.key_filename = get_cert_path(private=True)
    _add_config_file("sshd_config_dev", "/etc/ssh/sshd_config", "root", chmod="600")
    sudo("sudo systemctl restart ssh")


def change_root_password():
    crypted_password = crypt(ROOT_PASSWORD, 'salt')
    sudo('usermod --password %s %s' % (crypted_password, "root"), pty=False)


def install_pip():
    # sudo("dpkg --configure -a")
    sudo("apt-get update")
    sudo("apt-get install -y curl")
    sudo("curl --silent --show-error --retry 5 https://bootstrap.pypa.io/" "get-pip.py | sudo python3")


def install_samba():
    sudo("apt-get -y install samba")
    _add_config_file("smb.conf", "/etc/samba/smb.conf", "root")
    sudo("/etc/init.d/samba restart")
    sudo("smbpasswd -a %s" % NEW_USERNAME)


def install_extra_libs():
    sudo("apt-get update")
    sudo("apt-get -y install ntp autossh git")
    sudo('pip install pyudev')


def install_docker():

    # install docker
    sudo("curl -sSL get.docker.com | sh")

    # fix the docker host in json problem
    _add_config_file("docker.service", "/lib/systemd/system/docker.service", "root", chmod=755)

    # config deamon
    _add_config_file("daemon.json", "/etc/docker/daemon.json", "root")

    # sets up service
    sudo("systemctl enable docker")
    # sudo("groupadd docker")
    # allows users to use to use docker
    sudo("usermod -aG docker %s" % NEW_USERNAME)
    # installs docker compose
    sudo("pip install docker-compose")


def remove_bloat():
    sudo('apt update')
    sudo("apt-get -y remove --purge libreoffice*")
    sudo("apt-get -y remove --purge wolfram*")
    sudo("apt-get -y remove modemmanager")
    sudo("apt-get -y remove --purge minecraft*")
    sudo("apt-get -y purge --auto-remove scratch")
    sudo("dpkg --remove flashplugin-installer")
    sudo("apt-get clean")
    sudo("apt-get autoremove")


def set_hostname():
    sudo("sed -i 's/%s/%s/g' /etc/hostname" % (ORIGINAL_HOSTNAME, NEW_HOSTNAME))
    sudo("sed -i 's/%s/%s/g' /etc/hosts" % (ORIGINAL_HOSTNAME, NEW_HOSTNAME))
    sudo("hostname %s" % NEW_HOSTNAME)


def set_boot_config(config):
    if config == "kedei":
        _add_config_file("kedei_config.txt", "/boot/config.txt", "root")
    else:
        _add_config_file("config.txt", "/boot/config.txt", "root")


def add_resize():
    sudo('printf " quiet init=/usr/lib/raspi-config/init_resize.sh" >> /boot/cmdline.txt')
    _add_config_file("resize2fs_once", "/etc/init.d/resize2fs_once", "root", chmod="+x")
    sudo("systemctl enable resize2fs_once")

def _add_config_file(name, dst, owner, chmod=None):
    put("config_files/%s" % name, dst, use_sudo=True)
    if chmod is not None:
        sudo("chmod %s %s" % (chmod, dst))
    sudo("chown %s %s" % (owner, dst))
    sudo("chgrp %s %s" % (owner, dst))


def _add_software_file(name, dst, owner, chmod=755):
    put("software/%s" % name, dst, use_sudo=True)
    sudo("chmod %s %s" % (chmod, dst))
    sudo("chown %s %s" % (owner, dst))
    sudo("chgrp %s %s" % (owner, dst))

def reboot():
    print('System reboot')
    sudo('reboot')

def halt():
    print('System halt')
    sudo('halt')

def waveshare_install_SPI_touchscreen_drivers():
    waveshare_download_touchscreen_driver()
    waveshare_install_touchscreen_driver()

def fix_install():
    sudo("apt --fix-broken install")

def waveshare_download_touchscreen_driver():

    # git clone https://github.com/waveshare/LCD-show.git
    print('Downloading Waveshare touchscreen drivers. This operation may take a very long time')
    if not exists('/opt/waveshare', use_sudo=True):
        sudo('mkdir /opt/waveshare')
    sudo('cd /opt/waveshare ; git clone https://github.com/waveshare/LCD-show.git')
    sudo('pwd')

def waveshare_install_touchscreen_driver():
    if exists('/opt/waveshare/LCD-show', use_sudo=True):
        print('Installing Waveshare touchscreen driver')

        # Enable I2C
        # See https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c#installing-kernel-support-manually
        sudo('echo "dtparam=i2c1=on" | sudo tee -a /boot/config.txt')
        sudo('echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt')
        sudo('echo "i2c-bcm2708" | sudo tee -a /etc/modules')
        sudo('echo "i2c-dev" | sudo tee -a /etc/modules')

        # Disable Serial Console
        sudo('sudo sed -i \'s/console=serial0,115200//\' /boot/cmdline.txt')
        sudo('sudo sed -i \'s/console=ttyAMA0,115200//\' /boot/cmdline.txt')
        sudo('sudo sed -i \'s/kgdboc=ttyAMA0,115200//\' /boot/cmdline.txt')

        sudo('cd /opt/waveshare/LCD-show ; ./LCD35B-show-V2')
        print('Installing new kernel for Waveshare touchscreen driver completed')

def kedei_install_SPI_touchscreen_drivers():
    kedei_copy_touchscreen_drivers()
    # kedei_download_touchscreen_drivers()
    kedei_untar_touchscreen_drivers()
    kedei_backup_old_kernel()
    kedei_install_new_kernel()
    reboot()

def kedei_download_touchscreen_drivers():
    print('Downloading KeDei touchscreen drivers. This operation may take a very long time')
    if not exists('/opt/kedei', use_sudo=True):
        sudo('mkdir /opt/kedei')
    sudo('cd /opt/kedei ; wget http://www.kedei.net/raspberry/v6_1/LCD_show_v6_1_3.tar.gz')
    sudo('pwd')

def kedei_copy_touchscreen_drivers():
    print('Copying KeDei touchscreen drivers. This operation may take a very long time')
    if not exists('/opt/kedei', use_sudo=True):
        sudo('mkdir /opt/kedei')
    put('drivers/LCD_show_v6_1_3.tar.gz','/opt/kedei',use_sudo=True)

def kedei_untar_touchscreen_drivers():
    if exists('/opt/kedei', use_sudo=True):
        sudo('cd /opt/kedei ; tar zxvf LCD_show_v6_1_3.tar.gz')

def kedei_backup_old_kernel():
    if exists('/opt/kedei/LCD_show_v6_1_3', use_sudo=True):
        print('Backing up old kernel')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v /boot/kernel.img  ./backup/kernel.img')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v /boot/kernel7.img ./backup/kernel7.img')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v /boot/*.dtb ./backup/')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v /boot/overlays/*.dtb* ./backup/overlays/')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v -rf  /lib/firmware    ./backup/lib/')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v -rf  /lib/modules    ./backup/lib')
        print('Backing up old kernel completed')

def kedei_install_new_kernel():
    if exists('/opt/kedei/LCD_show_v6_1_3', use_sudo=True):
        print('Installing new kernel for Kedei touchscreen driver')

        # Enable I2C
        # See https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c#installing-kernel-support-manually
        sudo('echo "dtparam=i2c1=on" | sudo tee -a /boot/config.txt')
        sudo('echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt')
        sudo('echo "i2c-bcm2708" | sudo tee -a /etc/modules')
        sudo('echo "i2c-dev" | sudo tee -a /etc/modules')

        # Disable Serial Console
        sudo('sudo sed -i \'s/console=serial0,115200//\' /boot/cmdline.txt')
        sudo('sudo sed -i \'s/console=ttyAMA0,115200//\' /boot/cmdline.txt')
        sudo('sudo sed -i \'s/kgdboc=ttyAMA0,115200//\' /boot/cmdline.txt')

        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v ./lcd_35_v/kernel.img /boot/kernel.img')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v ./lcd_35_v/kernel7.img /boot/')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v ./lcd_35_v/*.dtb /boot/')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v ./lcd_35_v/overlays/*.dtb* /boot/overlays/')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v -rf ./lcd_35_v/lib/* /lib/')
        sudo('apt-mark hold raspberrypi-kernel')
        print('Installing new kernel for Kedei touchscreen driver completed')

def kedei_restore_old_kernel():
    if exists('/opt/kedei/LCD_show_v6_1_3', use_sudo=True):
        print('Restoring old kernel')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v ./backup/kernel.img /boot/kernel.img')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v ./backup/kernel7.img /boot/')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v ./backup/*.dtb /boot/')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v ./backup/overlays/*.dtb* /boot/overlays/')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v -rf ./backup/lib/* /lib/')
        print('Restoring old kernel completed')

def kedei_restore_hdmi_kernel():
    if exists('/opt/kedei/LCD_show_v6_1_3', use_sudo=True):
        print('Restoring kernel with HDMI output')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v ./hdmi/kernel.img /boot/kernel.img')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v ./hdmi/kernel7.img /boot/')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v ./hdmi/*.dtb /boot/')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v ./hdmi/overlays/*.dtb* /boot/overlays/')
        sudo('cd /opt/kedei/LCD_show_v6_1_3 ; cp -v -rf ./hdmi/lib/* /lib/')
        print('Restoring kernel with HDMI output completed')

def install_dev_apt_prerequisites():
    print('Installing software APT prerequisites')
    sudo('apt-get -y remove python-pip python3-pip ; apt-get -y --allow-unauthenticated install python-pip python3-pip')
    sudo('apt-get -y install python-requests python-pygame libts-bin libsdl1.2-dev libsdl-image1.2-dev libsdl-ttf2.0-dev')
    sudo('apt-get -y install python-requests python-numpy python-scipy python3-numpy python3-scipy')
    sudo('apt-get -y install ntpdate screen ntp ifmetric p7zip-full man apt-utils expect wget git libfreetype6 dbus dbus-*dev ')
    sudo('apt-get -y install uuid libsmbclient libssh-4 libpcre3 fonts-freefont-ttf espeak alsa-tools alsa-utils')
    sudo('apt-get -y install python3-gpiozero python-rpi.gpio python-pigpio python-gpiozero')
    sudo('apt-get -y install pigpio python3-pigpio python3-rpi.gpio raspi-gpio wiringpi')
    sudo('apt-get -y install fbset fbi i2c-tools avahi-utils')
    sudo('apt-get -y install omxplayer ola ola-python')
    sudo('apt-get -y install build-essential python3-dev')
    print('Installing software APT prerequisites completed')

def install_dev_pip_prerequisites():
    print('Installing software PIP prerequisites')
    # sudo('apt-get -y remove python-pip python3-pip ; apt-get -y install python-pip python3-pip')
    # sudo('pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pygameui') # not working
    # sudo('pip install evdev')
    # sudo('pip install tinkerforge')
    # #sudo('pip install numpy') # numpy is already installed by pygame
    # sudo('pip install pysrt')
    # sudo('pip install phue')
    # sudo('pip install pytz')
    # sudo('pip install apscheduler')
    # sudo('pip install pygameui')
    # sudo('pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org  pygameui') # not working
    install_pygameui()
    sudo('pip3 install evdev')
    sudo('pip3 install tinkerforge')
    sudo('pip3 install pysrt')
    sudo('pip3 install phue')
    sudo('pip3 install pytz')
    sudo('pip3 install apscheduler')
    sudo('pip3 install dbus-python')
    sudo('pip3 install flask')
    sudo('pip3 install -U flask-cors')
    sudo('pip3 install Flask-RESTful')
    sudo('pip3 install Flask-Jsonpify')
    sudo('pip3 install flask-inputs')
    sudo('pip3 install omxplayer-wrapper')
    print('Installing software PIP prerequisites completed')

def install_pygameui():
    print('Installing pygameui')
    if not exists('/opt/pygameui', use_sudo=True):
        sudo('mkdir /opt/pygameui')
    sudo('cd /opt/pygameui ; git clone https://github.com/fictorial/pygameui.git /opt/pygameui')
    sudo('cd /opt/pygameui ; python setup.py install')
    print('Installing pygameui completed')

def install_rclone():
    print('Installing rclone')
    if not exists('/opt/rclone', use_sudo=True):
        sudo('mkdir /opt/rclone')
    sudo('cd /opt/rclone ; wget --no-check-certificate https://raw.github.com/pageauc/rclone4pi/master/rclone-install.sh')
    sudo('cd /opt/rclone ; chmod +x ./rclone-install.sh ; ./rclone-install.sh')
    sudo('rclone --version')
    print('Installing rclone clompleted')

def install_tinkerforge_brickd():
    print('Installing Tinkerforge brickd')
    if not exists('/opt/brickd', use_sudo=True):
        sudo('mkdir /opt/brickd')
    sudo('cd /opt/brickd ; wget http://download.tinkerforge.com/tools/brickd/linux/brickd-2.3.2_armhf.deb')
    sudo('cd /opt/brickd ; dpkg -i brickd-2.3.2_armhf.deb')
    print('Installing Tinkerforge brickd clompleted')



def erase_usb_stick():
    print('Erasing all files from /media/usb')
    sudo('rm -rf /media/usb/*')
    print('Erasing all files from /media/usb completed')

def create_lushroom_dev():
    print('Creating LushRoom development environment')
    if not exists('/opt/lushroom', use_sudo=True):
        sudo('mkdir /opt/lushroom')
    if not exists('/opt/lushroom/lrpi_base', use_sudo=True):
        sudo('mkdir /opt/lushroom/lrpi_base')
        sudo('git clone --single-branch -b master https://github.com/LUSHDigital/lrpi_base.git /opt/lushroom/lrpi_base')
    if not exists('/opt/lushroom/lrpi_bootstrap', use_sudo=True):
        sudo('mkdir /opt/lushroom/lrpi_bootstrap')
        sudo('git clone --single-branch -b master https://github.com/LUSHDigital/lrpi_bootstrap.git /opt/lushroom/lrpi_bootstrap')
    if not exists('/opt/lushroom/lrpi_commands', use_sudo=True):
        sudo('mkdir /opt/lushroom/lrpi_commands')
        sudo('git clone --single-branch -b master https://github.com/LUSHDigital/lrpi_commands.git /opt/lushroom/lrpi_commands')
    if not exists('/opt/lushroom/lrpi_rclone', use_sudo=True):
        sudo('mkdir /opt/lushroom/lrpi_rclone')
        sudo('git clone --single-branch -b master https://github.com/LUSHDigital/lrpi_rclone.git /opt/lushroom/lrpi_rclone')
    if not exists('/opt/lushroom/lrpi_player', use_sudo=True):
        sudo('mkdir /opt/lushroom/lrpi_player')
        sudo('git clone --single-branch -b master https://github.com/LUSHDigital/lrpi_player.git /opt/lushroom/lrpi_player')
    if not exists('/opt/lushroom/lrpi_record', use_sudo=True):
        sudo('mkdir /opt/lushroom/lrpi_record')
        sudo('git clone --single-branch -b master https://github.com/LUSHDigital/lrpi_record.git /opt/lushroom/lrpi_record')
    if not exists('/opt/lushroom/lrpi_tablet_ui', use_sudo=True):
        sudo('mkdir /opt/lushroom/lrpi_tablet_ui')
        sudo('git clone --single-branch -b master https://github.com/LUSHDigital/lrpi_tablet_ui.git /opt/lushroom/lrpi_tablet_ui')
    if not exists('/opt/lushroom/lrpi_display', use_sudo=True):
        sudo('mkdir /opt/lushroom/lrpi_display')
        sudo('git clone --single-branch -b master https://github.com/LUSHDigital/lrpi_display.git /opt/lushroom/lrpi_display')

    print('Creating LushRoom development environment completed')



def reduce_writes():

    # a set of optimisations from
    # http://www.zdnet.com/article/raspberry-pi-extending-the-life-of-the-sd-card/
    # and
    # https://narcisocerezo.wordpress.com/2014/06/25/create-a-robust-raspberry-pi-setup-for-24x7-operation/

    # minimise writes
    use_ram_partitions()
    _stop_fsck_running()
    # _redirect_logrotate_state()
    # _dont_update_fake_hwclock()
    # _dont_do_man_indexing()
    _remove_swap()

def use_ram_partitions():
    sudo('echo "tmpfs    /tmp    tmpfs    defaults,noatime,nosuid,size=100m    0 0" >> /etc/fstab')
    sudo('echo "tmpfs    /var/tmp    tmpfs    defaults,noatime,nosuid,size=30m    0 0" >> /etc/fstab')
    sudo('echo "tmpfs    /var/log    tmpfs    defaults,noatime,nosuid,mode=0755,size=100m    0" >> /etc/fstab')

def _redirect_logrotate_state():
    sudo("rm /etc/cron.daily/logrotate")
    _add_config_file("logrotate", "/etc/cron.daily/logrotate", "root", chmod="755")

def _stop_fsck_running():
    sudo("tune2fs -c -1 -i 0 /dev/mmcblk0p2")

def _dont_update_fake_hwclock():
    sudo("rm /etc/cron.hourly/fake-hwclock")

def _dont_do_man_indexing():
    sudo("rm  /etc/cron.weekly/man-db")
    sudo("rm  /etc/cron.daily/man-db")

def _remove_swap():
    # not needed on Hypriot OS
    sudo("update-rc.d -f dphys-swapfile remove")
    sudo("swapoff /var/swap")
    sudo("rm /var/swap")

def _reduce_logging():
    ## add our own rsyslog.conf
    sudo("rm /etc/rsyslog.conf")
    put("rsyslog.conf", "/etc/rsyslog.conf", use_sudo=True)
    sudo("chmod 755 /etc/rsyslog.conf")
    sudo("chown root /etc/rsyslog.conf")
    sudo("chgrp root /etc/rsyslog.conf")

def test():
    put("test.txt", "~")

def get_bashrc():
    get("/home/lush/.bashrc")


def add_bootstrap():

    env.password = None
    env.key_filename = get_cert_path(private=True)

    sudo("mkdir -p /opt/lushroom")

    file_names = ["start.sh",
                  "bootstrap.py",
                  "mount.py",
                  "monitor.py",
                  "clean_wifi.py",
                  "docker-tunnel.service.template"
                  ]

    for name in file_names:
        _add_software_file(name, "/opt/lushroom/%s" % name, "root")

    _add_config_file("lushroom-bootstrap.service", "/etc/systemd/system/lushroom-bootstrap.service", "root", chmod=755)

    # sets up service
    sudo("systemctl enable lushroom-bootstrap")



