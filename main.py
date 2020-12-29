#!/usr/bin/python3
# Digital Photo Frame by David Réchatin

from flask import Flask, render_template
import os
import shlex
from signal import SIGINT
import subprocess

from config import AppConfig, UserConfig
import utils

version = "0.1.0"
last_update = "27/12/2020"


def kill_fim_and_clear():
    """Kill all fmi processes"""
    if UserConfig.debug:
        print("Kill all fim processes and clear screen...")
    os.system("pkill -9 fim")
    os.system("dd if=/dev/zero of=/dev/fb0 >/dev/null 2>&1")  # clear screen


def execute_subprocess(command):
    if UserConfig.debug:
        print(command)
    p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8')

    try:
        outs, errs = p.communicate(timeout=UserConfig.display_time_in_sec + 10)
    except subprocess.TimeoutExpired:
        if UserConfig.debug:
            print("subprocess.TimeoutExpired")
        p.kill()
        outs, errs = p.communicate()

    if UserConfig.debug:
        print({"pid": p.pid, "outs": outs, "errs": errs})

    return {"pid": p.pid, "outs": outs, "errs": errs}


def display_one_photo(filename: str) -> dict:
    """Display a photo using the framebuffer
    Todo:
        * Remove 'fbi' command
    Args:
        filename (str): Path and filename of photo file to display.
    Returns:
        dict: {"pid": int, "outs": str, "errs": str}
    """

    if UserConfig.debug:
        print(f"Display photo : {filename}")

    command = f"fim {filename} --autozoom --execute-commands 'sleep {UserConfig.display_time_in_sec}; quit;'"
    if not UserConfig.debug:
        command.append("--quiet")

    pid, outs, errs = execute_subprocess(command)

    return {"pid": pid, "outs": outs, "errs": errs}


def start_slideshow():
    """Start slideshow
    Todo:
        * use display_one_photo() in a python loop instead of --slideshow
        * use many folders and subfolders
    """

    if UserConfig.debug:
        print("Start slideshow...")
    kill_fim_and_clear()

    # try natural sort
    # command = f"ls {AppConfig.path_media} -1v | fim --read-from-stdin --autozoom --slideshow {UserConfig.display_time_in_sec} -sort-basename --execute-commands 'sleep {UserConfig.display_time_in_sec}; quit;'"
    command = f"fim {AppConfig.path_media} --autozoom --sort-basename --execute-commands 'while(_fileindex<_filelistlen){{sleep {UserConfig.display_time_in_sec}; next; sleep {UserConfig.display_time_in_sec}; quit;}}'"
    if UserConfig.random_order:
        command += " --random"
    if not UserConfig.debug:
        command += " --quiet"

    pid, outs, errs = execute_subprocess(command)

    return {"pid": pid, "outs": outs, "errs": errs}


def stop_slideshow():
    """Stop slideshow"""
    kill_fim_and_clear()


http_server = Flask(__name__)


@http_server.route('/')
def index():
    return render_template('index.html')


@http_server.route('/start-slideshow')
def http_start_slideshow():
    start_slideshow()
    return 'start_slideshow'


@http_server.route('/stop-slideshow')
def http_stop_slideshow():
    stop_slideshow()
    return 'stop_slideshow'


@http_server.route('/display-one-photo/<filename>')
def http_display_one_photo(filename):
    kill_fim_and_clear()
    display_one_photo(AppConfig.path_media + filename)
    return 'display_one_photo'


@http_server.route('/close')
def http_close():
    kill_fim_and_clear()
    # sys.exit() don't kill the main process
    os.kill(os.getpid(), SIGINT)


@http_server.route('/restart')
def http_restart():
    kill_fim_and_clear()
    os.system("sudo shutdown -r now")
    return 'restart'


@http_server.route('/poweroff')
def http_poweroff():
    kill_fim_and_clear()
    os.system("sudo shutdown -h now")
    return 'shutdown'


if __name__ == '__main__':
    """
    Todo:
        * manage wifi connection with python :
            - save wifi ssid and password in UserConfig
            - if no wifi in UserConfig, then create access point
        * isolate Flask http_server
    """

    kill_fim_and_clear()  # clear process + console + screen

    print("=================================================")
    print("-------------  DigitalPhotoFrame  ----------------------")
    print("-------------  by David Réchatin  ----------------------")
    print("------------- " + version + " " + last_update + " ------------------")
    print("=================================================")

    UserConfig.load_from_file()

    ip = utils.get_ip_address()
    print(f"My IP address is {ip}")

    start_slideshow()

    http_server.run(debug=UserConfig.debug, host=ip, port=AppConfig.http_port)

    exit()
