# -*- coding:utf-8 -*-
# !/usr/bin/env python
# Copyright 2017 Erik Selberg All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import re

from jira import JIRA
from jira.exceptions import JIRAError

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

def log(str):
    print(str)

def dbg(str):
    if verbose != 0 and verbose != "0":  # handle string config
        print(str)

# set these via heroku config:set FOO=bar        
verbose = os.environ.get('VERBOSE', 0)
user = os.environ.get('USER', "")
pw = os.environ.get('PASS', "")    # Yes, this sucks. Haven't had time to turn this into oauth or better
jirasite = os.environ.get("SITE", "")

options = {
    'server': 'https://' + jirasite + '.atlassian.net',
    'max_retries': 1
}

try:
    jira = JIRA(options, basic_auth = (user, pw))
except JIRAError as e:
    if e.status_code == 401:
        log("Login to JIRA failed, check your username / password (uname: " + user + ", pw: " + pw + ")")
        exit(-1)
        
@app.route('/webhook', methods=['POST'])
def webhook():

    dbg("Here we go!")

    req = request.get_json(silent=True, force=True)

    dbg("Request:")
    dbg(json.dumps(req, indent=4))

    res = processRequest(req)

    r = make_response("Success")
    return r


def processRequest(req):

    messages = "messages"
    res = {}
    
    if req.get(messages, "") == "":
        log("Messages is empty, bailing...\n")
        return {}
    else:
        dbg("Looks like a PagerDuty message!\n")

    try:
        for msg in req[messages]:
            if msg.get("type", "") != "incident.acknowledge":
                dbg("Couldn't figure out message type " + msg.get("type", "type_failed"))
                continue;
            
            dbg("Looks like an acknowledgement!")
                
            data = msg["data"]
            incident_key = data["incident"].get("incident_key", "")
            if re.match(r"^[A-Z0-9]+-[0-9]+$", incident_key) == 0: 
                dbg("Didn't find Jira incident key " + incident_key)
                continue
            dbg("Found Jira incident key " + incident_key)
                
            assigned_user = data["incident"]["assigned_to_user"]["email"]
            dbg("Assigned to user is: " + assigned_user)

            issue = jira.issue(incident_key)
            users = jira.search_users(assigned_user)
            if len(users) == 0:
                log("Unable to find user " + assigned_user + " in Jira")
                continue
                
            uname = users[0].name
            jira.assign_issue(incident_key, uname)
            log("Assigning Jira issue " + incident_key + " to Jira user " + uname)
            res = {"Success" : "\"" + incident_key + " " + uname + "\""}

    except Exception as inst:
        log("Try failed!")
        log(type(inst))    # the exception instance
        log(inst.args)     # arguments stored in .args
        log(inst)          # __str__ allows args to be printed directly,

    return res


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    log("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
