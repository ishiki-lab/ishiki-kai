from crypt import crypt
from fabric.api import local, settings, abort, run, env, sudo, put, get, prefix
from fabric.contrib.files import exists

# from fabric import Connection, Config, task
# import getpass

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from config import PI_PASSWORD

# env.hosts = ["%s:%s" % ("raspberrypi.local", 22)]
env.hosts = ["%s:%s" % ("lushroom1-pi.local", 22)]
env.user = "lush"
env.password = PI_PASSWORD

# HOST = "192.168.1.101"
# PORT = 22
# USER = "pi"

# sudo_pass = getpass.getpass("What's your sudo password?")
# configuration = Config(overrides={'sudo': {'password': sudo_pass}})
# c = Connection(host=HOST, user=USER, port=PORT, config=configuration)
# c = Connection(host=HOST, user=USER, port=PORT)

# BOOTSTRAP_VERSION = "0.0.1"
# PYTHON_VERSION = "0.0.2"
# TEST_VERSION = "0.0.1"
# DESKCONTROL_VERSION = "0.0.6"
# BRICKD_VERSION = "0.0.1"
# COMMAND_VERSION = "0.0.4"

# Raspbian supporting KeDei touch screen
# http://www.kedei.net/raspberry/v6_1/rpi_35_v6_3_stretch_kernel_4_15_18.rar
RASPBIAN_VERSION = "KeDei Raspbian rpi_v6_3_stretch_kernel_4_15_18"

############################################################################
##              Preparing the base disc image from JESSIE_VERSION
############################################################################

"""
    On local machine install fabric3
    pip3 install fabric3
    Steps to set up the Raspberry Pi:
    Login to Raspberry Pi
    "sudo su"
    'wpa_passphrase "WiFiSSID" "WiFiPassword" >> /etc/wpa_supplicant/wpa_supplicant.conf'
    "wpa_cli reconfigure"
    "raspi-config"
    Interfacing Options > SSH > Yes
    reboot
"""

def list_usb():
    sudo('ls /media/usb/')

def prepare_card():
    uninstall_packages()
    apt_autoremove()
    apt_update()
    apt_upgrade()
    apt_autoremove()
    apt_clean()
    # install_openhab()
    # change_password()
    # _change_graphics_memory()
    # install_docker()
    # docker_login(password)
    # add_bootstrap()
    # _reduce_logging()
    reduce_writes()
    # add_resize()
    # sudo("reboot")

def apt_update():
    sudo('apt update')

def apt_upgrade():
    sudo('apt upgrade')

def apt_autoremove():
    sudo('apt autoremove')

def apt_clean():
    sudo('df -h')
    sudo('apt clean')
    sudo('df -h')

def uninstall_packages():
    sudo('df -h')
    sudo('apt remove wolfram*')
    sudo('apt remove scratch*')
    sudo('apt remove libreoffice*')
    sudo('apt remove minecraft*')
    sudo('df -h')

def reboot():
    print('System reboot')
    sudo('reboot')

def halt():
    print('System halt')
    sudo('halt')

def kedei_install_SPI_touchscreen_drivers():
    pass
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
    sudo('apt-get -y install libsmbclient libssh-4 libpcre3 fonts-freefont-ttf espeak alsa-tools alsa-utils')
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
    sudo('pip install evdev')
    sudo('pip install tinkerforge')
    #sudo('pip install numpy') # numpy is already installed by pygame
    sudo('pip install pysrt')
    sudo('pip install phue')
    sudo('pip install pytz')
    sudo('pip install apscheduler')
    sudo('pip install pygameui')
    # sudo('pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org  pygameui') # not working
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

# def install_pygameui():
#     print('Installing pygameui')
#     if not exists('/opt/pygameui', use_sudo=True):
#         sudo('mkdir /opt/pygameui')
#     sudo('cd /opt/pygameui ; git clone https://github.com/fictorial/pygameui.git /opt/pygameui')
#     sudo('cd /opt/pygameui ; python setup.py install')
#     print('Installing pygameui completed')

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

def install_openhab():
    sudo('apt install screen mc vim git htop')
    sudo('wget -qO - "https://bintray.com/user/downloadSubjectPublicKey?username=openhab" | apt-key add')
    sudo('apt-get install apt-transport-https')
    sudo('echo "deb https://dl.bintray.com/openhab/apt-repo2 stable main" | tee /etc/apt/sources.list.d/openhab2.list')
    sudo('apt-get update')
    sudo('apt-get install openhab2')
    sudo('apt-get install openhab2-addons')
    sudo('systemctl start openhab2.service')
    sudo('systemctl status openhab2.service')
    sudo('systemctl daemon-reload')
    sudo('systemctl enable openhab2.service')

def reduce_writes():

    # a set of optimisations from
    # http://www.zdnet.com/article/raspberry-pi-extending-the-life-of-the-sd-card/
    # and
    # https://narcisocerezo.wordpress.com/2014/06/25/create-a-robust-raspberry-pi-setup-for-24x7-operation/

    # minimise writes
    use_ram_partitions()
    _stop_fsck_running()
    _redirect_logrotate_state()
    _dont_update_fake_hwclock()
    _dont_do_man_indexing()
    # _remove_swap()

def use_ram_partitions():
    sudo('echo "tmpfs    /tmp    tmpfs    defaults,noatime,nosuid,size=100m    0 0" >> /etc/fstab')
    sudo('echo "tmpfs    /var/tmp    tmpfs    defaults,noatime,nosuid,size=30m    0 0" >> /etc/fstab')
    sudo('echo "tmpfs    /var/log    tmpfs    defaults,noatime,nosuid,mode=0755,size=100m    0" >> /etc/fstab')

def _redirect_logrotate_state():
    sudo("rm /etc/cron.daily/logrotate")
    put("logrotate", "/etc/cron.daily/logrotate", use_sudo=True)
    sudo("chmod 755 /etc/cron.daily/logrotate")
    sudo("chown root /etc/cron.daily/logrotate")
    sudo("chgrp root /etc/cron.daily/logrotate")

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

def change_password():
    env.password = "raspberry"
    crypted_password = crypt(PI_PASSWORD, 'salt')
    sudo('usermod --password %s %s' % (crypted_password, env.user), pty=False)

def _change_graphics_memory():
    sudo('echo "gpu_mem=256" >> /boot/config.txt')

def add_bootstrap():
    # # build_bootstrap()
    # sudo("mkdir -p /opt/lushroom")
    # put("start.sh", "/opt/lushroom/start.sh", use_sudo=True)
    # sudo("chmod 755 /opt/lushroom/start.sh")

    put("bootstrap.py", "/opt/lushroom/bootstrap.py", use_sudo=True)
    sudo("chmod 755 /opt/lushroom/bootstrap.py")

    # ## add our own rc.local
    # sudo("rm /etc/rc.local")
    # put("rc.local", "/etc/rc.local", use_sudo=True)
    # sudo("chmod 755 /etc/rc.local")
    # sudo("chown root /etc/rc.local")
    # sudo("chgrp root /etc/rc.local")

"""

def add_resize():
    sudo('printf " quiet init=/usr/lib/raspi-config/init_resize.sh" >> /boot/cmdline.txt')
    put("resize2fs_once", "/etc/init.d/resize2fs_once", use_sudo=True)
    sudo("chmod +x /etc/init.d/resize2fs_once")
    sudo("chown root /etc/init.d/resize2fs_once")
    sudo("chgrp root /etc/init.d/resize2fs_once")
    sudo("systemctl enable resize2fs_once")

def build_bootstrap():
    tag = BOOTSTRAP_VERSION
    put("docker", "~")
    sudo('docker build --no-cache=true -t="lushroom/lushroom-bootstrap:%s" '
         'docker/lushroom-bootstrap' % tag)
    sudo('docker tag lushroom/lushroom-bootstrap:%s lushroom/'
         'lushroom-bootstrap:latest' % tag)
    sudo('docker push lushroom/lushroom-bootstrap:latest')

def install_docker():
    # install docker
    run("curl -sSL get.docker.com | sh")
    # sets up service
    run("sudo systemctl enable docker")
    # allows pi use to use docker
    run("sudo usermod -aG docker pi")
    # installs docker compose
    sudo("curl --silent --show-error --retry 5 https://bootstrap.pypa.io/"
         "get-pip.py | sudo python2.7")
    sudo("pip install docker-compose")


############################################################################
##              Docker commands for building other images                 ##
############################################################################


def docker_login(password):
    sudo('docker login -u arupiot -p "%s"' % password)


def push_bootstrap():
    sudo('docker push lushroom/lushroom-bootstrap:latest')


def build_python():
    tag = PYTHON_VERSION
    put("docker", "~")
    sudo('docker build --no-cache=true -t="lushroom/lushroom-python:%s" docker/lushroom-python' % tag)
    sudo('docker push lushroom/lushroom-python:%s' % tag)
    sudo('docker tag lushroom/lushroom-python:%s lushroom/lushroom-python:latest' % tag)
    sudo('docker push lushroom/lushroom-python:latest')


def build_deskcontrol():
    tag = DESKCONTROL_VERSION
    put("docker", "~")
    sudo('docker build --no-cache=true -t="lushroom/lushroom-deskcontrol:%s" docker/lushroom-deskcontrol' % tag)
    sudo('docker push lushroom/lushroom-deskcontrol:%s' % tag)
    sudo('docker tag lushroom/lushroom-deskcontrol:%s lushroom/lushroom-deskcontrol:latest' % tag)
    sudo('docker push lushroom/lushroom-deskcontrol:latest')


def build_command():
    tag = COMMAND_VERSION
    put("docker", "~")
    sudo('docker build --no-cache=true -t="lushroom/lushroom-commands:%s" docker/lushroom-commands' % tag)
    sudo('docker push lushroom/lushroom-commands:%s' % tag)
    sudo('docker tag lushroom/lushroom-commands:%s lushroom/lushroom-commands:latest' % tag)
    sudo('docker push lushroom/lushroom-commands:latest')


def build_brickd():
    tag = BRICKD_VERSION
    put("docker", "~")
    sudo('docker build --no-cache=true -t="lushroom/lushroom-brickd:%s" docker/lushroom-brickd' % tag)
    sudo('docker push lushroom/lushroom-brickd:%s' % tag)
    sudo('docker tag lushroom/lushroom-brickd:%s lushroom/lushroom-brickd:latest' % tag)
    sudo('docker push lushroom/lushroom-brickd:latest')


"""
