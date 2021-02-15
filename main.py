#!/usr/bin/python3
# Digital Photo Frame by David Réchatin

from flask import Flask, render_template
import os
import re
import shlex
from signal import SIGINT
import subprocess
from time import sleep

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


def execute_subprocess(command, stdin=None):
    if stdin:
        stdin = stdin.encode()  # encode the string to be compatible with stdin

    if UserConfig.debug:
        print("command :", command)
        print("stdin :", stdin)

    p = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # todo : p.communicate wait the complete execution of subprocess
    stdout_data, stderr_data = p.communicate(input=stdin)

    r = dict()
    r["pid"] = p.pid
    r["stdout"], r["stderr"] = stdout_data.decode(), stderr_data.decode()

    if UserConfig.debug:
        print(r)

    return r


def display_one_photo(filename: str) -> dict:
    """Display a photo using the framebuffer
    Args:
        filename (str): Path and filename of photo file to display.
    Returns:
        dict: {"pid": int, "outs": str, "errs": str}
    """

    if UserConfig.debug:
        print(f"Display photo : {filename}")

    command = f"fim {filename} --autozoom --execute-commands 'sleep {UserConfig.display_time_in_sec}; quit;'"
    if not UserConfig.debug:
        command += "--quiet"

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

    media_list = os.listdir(AppConfig.path_media)
    media_list.sort(key=lambda f: int(re.sub("\D", "", f)))
    media_list = [os.path.join(AppConfig.path_media, filename) for filename in media_list]
    stdin = '\n'.join(media_list)

    # command = f"fim {AppConfig.path_media} --autozoom --sort-basename --execute-commands 'while(_fileindex<_filelistlen){{sleep {UserConfig.display_time_in_sec}; next; sleep {UserConfig.display_time_in_sec}; quit;}}'"
    command = f"fim --read-from-stdin --autozoom --execute-commands 'while(_fileindex<_filelistlen){{sleep {UserConfig.display_time_in_sec}; next; sleep {UserConfig.display_time_in_sec}; quit;}}'"
    if UserConfig.random_order:
        command += " --random"
    if not UserConfig.debug:
        command += " --quiet"

    r = execute_subprocess(command, stdin)

    return r


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


def start_slideshow2():
    """Start slideshow
    Todo:
        * use display_one_photo() in a python loop instead of --slideshow
        * use many folders and subfolders
    """

    if UserConfig.debug:
        print("Start slideshow...")
    kill_fim_and_clear()

    media_list = os.listdir(AppConfig.path_media)
    media_list.sort(key=lambda f: int(re.sub("\D", "", f)))
    media_list = [os.path.join(AppConfig.path_media, filename) for filename in media_list]
    stdin = '\n'.join(media_list)

    # command = f"fim {AppConfig.path_media} --autozoom --sort-basename --execute-commands 'while(_fileindex<_filelistlen){{sleep {UserConfig.display_time_in_sec}; next; sleep {UserConfig.display_time_in_sec}; quit;}}'"
    command = f"fim --read-from-stdin --autozoom"
    if UserConfig.random_order:
        command += " --random"
    if not UserConfig.debug:
        command += " --quiet"


    if stdin:
        stdin = stdin.encode()
        stdin = media_list[0].encode()
        # encode the string to be compatible with stdin

    if UserConfig.debug:
        print("command :", command)
        print("stdin :", stdin)
        
    import pexpect

    p = pexpect.spawn("fim --read-from-stdin --autozoom", encoding='utf-8')

    #p = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # todo : p.communicate wait the complete execution of subprocess
    for media in media_list:
        print(media)
        stdin = media.encode()
        #stdout_data, stderr_data = p.communicate(input=stdin)
        p.sendline(media)
        print("Sleep...")
        sleep(UserConfig.display_time_in_sec)

    # r = dict()
    # r["pid"] = p.pid
    # r["stdout"], r["stderr"] = stdout_data.decode(), stderr_data.decode()

    # if UserConfig.debug:
    #     print(r)

    return None


def start_slideshow3():
    """Start slideshow
    Todo:
        * use display_one_photo() in a python loop instead of --slideshow
        * use many folders and subfolders
    """

    from framebuffer import Framebuffer
    from PIL import Image, ImageDraw


    if UserConfig.debug:
        print("Start slideshow...")
    kill_fim_and_clear()

    media_list = os.listdir(AppConfig.path_media)
    media_list.sort(key=lambda f: int(re.sub("\D", "", f)))
    media_list = [os.path.join(AppConfig.path_media, filename) for filename in media_list]
    stdin = '\n'.join(media_list)

    # command = f"fim {AppConfig.path_media} --autozoom --sort-basename --execute-commands 'while(_fileindex<_filelistlen){{sleep {UserConfig.display_time_in_sec}; next; sleep {UserConfig.display_time_in_sec}; quit;}}'"
    command = f"fim --read-from-stdin --autozoom"
    if UserConfig.random_order:
        command += " --random"
    if not UserConfig.debug:
        command += " --quiet"

    if stdin:
        stdin = stdin.encode()
        stdin = media_list[0].encode()
        # encode the string to be compatible with stdin

    if UserConfig.debug:
        print("command :", command)
        print("stdin :", stdin)

    import pexpect

    #p = pexpect.spawn("fim --read-from-stdin --autozoom", encoding='utf-8')

    # p = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # todo : p.communicate wait the complete execution of subprocess
    for media in media_list:
        print(media)
        stdin = media.encode()
        # stdout_data, stderr_data = p.communicate(input=stdin)



        fb = Framebuffer(0)
        image = Image.open(media).convert(mode="RGB")
        image.thumbnail(fb.size)
        print(image, image.mode)

        target = Image.new(mode="RGB", size=fb.size)
        assert image.size <= target.size
        box = ((target.size[0] - image.size[0]) // 2,
               (target.size[1] - image.size[1]) // 2)
        target.paste(image, box)
        fb.show(target)

    # r = dict()
    # r["pid"] = p.pid
    # r["stdout"], r["stderr"] = stdout_data.decode(), stderr_data.decode()

    # if UserConfig.debug:
    #     print(r)

    return None

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

    start_slideshow3()

    http_server.run(debug=UserConfig.debug, host=ip, port=AppConfig.http_port)

    exit()
