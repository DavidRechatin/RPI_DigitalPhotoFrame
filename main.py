#!/usr/bin/python
# coding=utf8
# Digital Photo Frame by David Réchatin

import os
import time
import commands
import subprocess
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import json
from multiprocessing import Process, Queue
import urllib2

version = "0.0.2"
last_update = "29/12/2015"

# --------------------------------------------------------------
# This section is defined by installer
debug = True
mouse_enable = False  # show mouse cursor
# --------------------------------------------------------------

# Variables list
today = ''                    # le current date (yyyy-mm-dd)

pathApp = "/home/pi/"        # path of E2ms scripts
fileConfig = ""     #
pathMedia = ""  #

ip = ''                         # current local ip address

config = []                # configuration of the device (from fileConfig)


# --------------------------------------------------------------

print "================================================="
print "-------------  DigitalPhotoFrame by David Réchatin  ----------------------"
print "------------- " + version + " " + last_update + " ------------------"
print "================================================="


# The HTTP server
class HTTPHandler (SimpleHTTPRequestHandler):
    server_version = "MonServeurHTTP/0.1"

    def do_GET(self):
        if self.path.find('.py') != -1:
            self.reponse()
        else:
            SimpleHTTPRequestHandler.do_GET(self)

    def reponse(self):
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("ok")
        html_return = http_request(self.path)
        self.wfile.write(html_return)


# Treatment of HTTP request
def http_request(http_req):
    if http_req != "":
        print http_req
        if http_req.find('?') != -1:
            page, arg = http_req.split('?', 1)
            arg = arg.split("&")
            arg_dict = {}
            for i in range(0, len(arg)):
                x, y = arg[i].split("=")
                arg_dict[x] = y
            arg = arg_dict
        else:
            page = http_req
            arg = ''
        page = page[1:-3]

        http_return = ""
        if page == "config":
            if debug:
                print "A remote configuration request has arrived."
                print "Arguments", arg
            queue_http_request.put({"config": arg})
        elif page == "test":
            if debug:
                print "A remote test request has arrived."
            http_return = test()
        elif page == "show":
            if debug:
                print "A remote show request has arrived."
                print "Arguments", arg
            queue_http_request.put({"show": arg})
        elif page == "showall":
            if debug:
                print "A remote show request has arrived."
                print "Arguments", arg
            queue_http_request.put({"showall": "True"})
        elif page == "restart":
            if debug:
                print "A remote restart request has arrived."
            queue_http_request.put({"restart": "True"})
        elif page == "shutdown":
            if debug:
                print "A remote shutdown request has arrived."
            queue_http_request.put({"shutdown": "True"})
        elif page == "exit":
            if debug:
                print "A remote exit request has arrived."
            queue_http_request.put({"exit": "True"})
        else:
            if debug:
                print "A unknown request has arrived."
        return "<br>" + http_return


# Get HTTP request
def http_send(url):
    req = urllib2.Request(url)
    try:
        urllib2.urlopen(req)
    except urllib2.URLError as e:
        print e.reason, "to", url


# http_request process
def proc_http_request(q_http_request):
    httpd = HTTPServer((ip, config['http_port']), HTTPHandler)
    httpd.serve_forever()


# Test command
def test():
    print "I test..."
    # cpu temperature
    check = commands.getoutput("vcgencmd measure_temp")
    print check
    return check


# Kill FBI command
def killfbi():
    print "I killing all fbi process..."
    os.system("sudo killall -9 fbi")


# Show all command
def showall():
    print "I show all photos..."
    os.system("fbi -T 1 -noverbose -readahead -autozoom -random -timeout 2 /home/pi/photos/*")


if __name__ == '__main__':

    # Defines all paths
    fileConfig = pathApp + "conf.json"
    pathMedia = pathApp + "photos/"

    # Read configuration file (json) > config[ ]
    try:
        json_data = open(fileConfig)
    except IOError:
        print "The configuration file is not found. This program must to be shutdown !"
        exit()
    config = json.load(json_data)
    json_data.close()
    if debug:
        print "The configuration this terminal is ", config

    # # Discover the local ip address >localIp
    proc = subprocess.Popen("/sbin/ifconfig  | grep 'inet adr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'",
                            shell=True, stdout=subprocess.PIPE)
    ip = proc.communicate()[0].replace('\n', '')
    print "My IP address is " + ip

    # start http_request process
    queue_http_request = Queue()
    worker_http_request = Process(target=proc_http_request, args=[queue_http_request])
    worker_http_request.start()

    # start fbi process
    showall()

    # main loop
    loop = True
    while loop:
        request = queue_http_request.get()
        print 'request:', request
        if "show" in request:
            killfbi()
            os.system("fbi -T 1 -noverbose -readahead -autozoom /home/pi/photos/" + request['show']['name'])
        elif "showall" in request:
            killfbi()
            showall()
        elif "exit" in request:
            killfbi()
            loop = False
        elif "restart" in request:
            os.system("sudo shutdown -r now")
        elif "shutdown" in request:
            os.system("sudo shutdown -h now")

    queue_http_request.close()
    worker_http_request.terminate()
    worker_http_request.join(1)
    exit()