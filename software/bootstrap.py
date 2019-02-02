import subprocess
import time
import socket
import shutil
import json
import os
import pwd
import grp
from mount import *

MOUNT_DIR = "/media/usb"
USERNAME = "lush"
WPA_SUPPLICANT_FILE = "/etc/wpa_supplicant/wpa_supplicant.conf"

def start():
    print("Bootstrap: Starting")

    # mount the usb
    if mount_usb():
        print("Found the Lushroom USB")
        settings_file = os.path.join(MOUNT_DIR, "settings.json")

        with open(settings_file, "r") as f:
            settings = json.loads(f.read())

        existing_settings_file = "/opt/lushroom/settings.json"
        if os.path.exists(existing_settings_file):
            with open(existing_settings_file, "r") as f:
                try:
                    existing_settings = json.loads(f.read())
                except Exception as e:
                    existing_settings = None
            os.remove(existing_settings_file)
        else:
            existing_settings = None

        # these functions must be idempotent and check first before updating anything

        # set wifi credentials
        ssid, psk = get_wifi_creds(settings)
        if ssid and not already_has_creds(ssid, psk):
            print("Bootstrap: Adding SSID=%s and PASSWORD=%s to wpa_supplicant.conf" % (ssid, psk))
            add_wifi_creds(ssid, psk)
        else:
            print("Bootstrap: Wifi already configured")

        # set hostname
        host_name = settings.get("host_name")
        if host_name:
            set_hostname(host_name)

        # set timezone
        time_zone = settings.get("time_zone")
        if time_zone:
            set_time_zone(time_zone)

        # set public/private keys
        public_key = settings.get("public_key")
        private_key = settings.get("private_key")
        if public_key and private_key:
            add_keys(public_key, private_key)

        # configure ssh tunnel
        tunnel_host = settings.get("tunnel_host")
        tunnel_port = settings.get("tunnel_port")
        tunnel_user = settings.get("tunnel_user")
        if tunnel_host and tunnel_port and tunnel_user:
            if existing_settings:
                existing_tunnel_host = existing_settings.get("tunnel_host")
                existing_tunnel_port = existing_settings.get("tunnel_port")
                if existing_tunnel_host != tunnel_host or existing_tunnel_port != tunnel_port:
                    print("Bootstrap: Docker tunnel")
                    configure_ssh_tunnel(tunnel_host, tunnel_port, tunnel_user)
                else:
                    print("Bootstrap: Docker tunnel already configured")
            else:
                print("Bootstrap: Docker Tunnel")
                configure_ssh_tunnel(tunnel_host, tunnel_port, tunnel_user)

        shutil.copy(settings_file, existing_settings_file)

    else:
        print("Failed to find the Lushroom USB")


def _replace_template_text(text, name, value):
    return text.replace("{{ %s }}" % name, value)


def configure_ssh_tunnel(tunnel_host, tunnel_port, tunnel_user):

    cmd = "systemctl stop docker-tunnel.service"
    subprocess.call(cmd, shell=True)

    with open("/opt/lushroom/docker-tunnel.service.template", "r") as f:
        template_text = f.read()

    template_text = _replace_template_text(template_text, "tunnel_host", tunnel_host)
    template_text = _replace_template_text(template_text, "tunnel_port", tunnel_port)
    conf_text = _replace_template_text(template_text, "tunnel_user", tunnel_user)

    conf_file_path = "/etc/systemd/system/docker-tunnel.service"

    if os.path.exists(conf_file_path):
        os.remove(conf_file_path)

    with open(conf_file_path, "w") as f:
        f.write(conf_text)

    os.chmod(conf_file_path, 755)

    cmd = "systemctl daemon-reload"
    subprocess.call(cmd, shell=True)
    cmd = "systemctl start docker-tunnel.service"
    subprocess.call(cmd, shell=True)
    cmd = "systemctl enable docker-tunnel.service"
    subprocess.call(cmd, shell=True)


def set_time_zone(time_zone):

    dst = "/etc/localtime"
    src = "/usr/share/zoneinfo/%s" % time_zone
    if os.path.exists(dst):
        if os.path.islink(dst):
            target = os.readlink(dst)
            if target == src:
                print("Bootstrap: Time zone already set")
                return
            else:
                os.remove(dst)
        else:
            os.remove(dst)
    print("Bootstrap: Setting time zone")
    os.symlink(src, dst)


def ensure_content_matches(file_path, content, mode, uid, gid):

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            existing_content = f.read()
        if existing_content == content:
            print("Bootstrap: File alread exists %s" % file_path)
            return
        else:
            os.remove(file_path)

    print("Bootstrap: Updating file %s" % file_path)
    with open(file_path, "w") as f:
        f.write(content)

    os.chmod(file_path, mode)
    os.chown(file_path, uid, gid)


def add_keys(public_key, private_key):

    ssh_dir = "/home/%s/.ssh" % USERNAME
    public_file = os.path.join(ssh_dir, "id_rsa.pub")
    private_file = os.path.join(ssh_dir, "id_rsa")
    uid = pwd.getpwnam(USERNAME).pw_uid
    gid = grp.getgrnam(USERNAME).gr_gid

    # ensure the dir
    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir, mode=700)
        os.chown(ssh_dir, uid, gid)

    ensure_content_matches(public_file, public_key, 644, uid, gid)
    ensure_content_matches(private_file, private_key, 600, uid, gid)


def add_wifi_creds(ssid, psk):
    cmd = 'wpa_passphrase "%s" "%s" >> /etc/wpa_supplicant/wpa_supplicant.conf' % (ssid, psk)
    subprocess.call(cmd, shell=True)
    time.sleep(1)
    cmd = "sudo wpa_cli reconfigure"
    subprocess.call(cmd, shell=True)
    time.sleep(3)


def get_wifi_creds(creds):
    return creds.get("ssid"), creds.get("psk")


def already_has_creds(ssid, psk):
    if os.path.exists(WPA_SUPPLICANT_FILE):
        with open(WPA_SUPPLICANT_FILE, "r") as f:
            existing = f.read()
        return  ssid in existing and psk in existing
    else:
        return False


def set_hostname(new_hostname):
    current_hostname = socket.gethostname()
    if new_hostname != current_hostname:
        print("Bootstrap: Setting host name")
        cmd = "sed -i 's/%s/%s/g' /etc/hostname" % (current_hostname, new_hostname)
        subprocess.call(cmd, shell=True)
        cmd = "sed -i 's/%s/%s/g' /etc/hosts" % (current_hostname, new_hostname)
        subprocess.call(cmd, shell=True)
        cmd = "hostname %s" % new_hostname
        subprocess.call(cmd, shell=True)
    else:
        print("Bootstrap: Host name already set")


def _list_files(root, result):
    for filename in os.listdir(root):
        path = os.path.join(root, filename)

        if os.path.isfile(path):
            if filename.startswith("settings"):
                result.append(path)
                break

        elif os.path.isdir(path):
            _list_files(path, result)


def mount_usb():

    devices = list_media_devices()
    found = []
    for device in devices:
        mount(device)
        if is_mounted(device):
            _list_files(get_media_path(device), found)
            if len(found) > 0:
                return True
            else:
                unmount(device)

    return False


if __name__ == '__main__':
    start()
