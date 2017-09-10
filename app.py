# -*- coding:utf-8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
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

def debug(str):
    if verbose:
        print(str)

# set these via heroku config:set FOO=bar        
verbose = os.environ.get('VERBOSE', 0)
user = os.environ.get('USER', "")
pw = os.environ.get('PASS', "")

options = {
    'server': 'https://cookbrite.atlassian.net'}
try:
    jira = JIRA(options, basic_auth = (user, pw))
except JIRAError as e:
    if e.status_code == 401:
        log("Login to JIRA failed, check your username / password (uname: " + user + "), pw: " + pw + ")")
        exit(-1)

        
@app.route('/webhook', methods=['POST'])
def webhook():

    debug("Here we go!")

    req = request.get_json(silent=True, force=True)

    debug("Request:")
    debug(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    #    r = make_response(res.get("Success", ""))
    #    r.headers['Content-Type'] = 'application/json'
    r = make_response("Success")
    return r


def processRequest(req):

    messages = "messages"
    res = {}
    
    if req.get(messages, "") == "":
        log("Messages is empty, bailing...\n")
        return {}
    else:
        debug("Looks like a PagerDuty message!\n")

    try:
        for msg in req[messages]:
            if msg.get("type", "") == "incident.acknowledge":
                debug("Looks like an acknowledgement!")
                
                data = msg["data"]
                incident_key = data["incident"].get("incident_key", "")
                if re.match(r"^[A-Z0-9]+-[0-9]+$", incident_key): # TODO: Jira REGEXP check
                    debug("Found Jira incident key " + incident_key)
                else:
                    debug("Didn't find Jira incident key " + incident_key)
                    return {}

                assigned_user = data["incident"]["assigned_to_user"]["email"]
                debug("Assigned to user is: " + assigned_user)

                issue = jira.issue(incident_key)
                users = jira.search_users(assigned_user)
                uname = ""
                if len(users):
                    uname = users[0].name

                    jira.assign_issue(incident_key, uname)
                    log("Assigning Jira issue " + incident_key + " to Jira user " + uname)
                    res = {"Success" : "\"" + incident_key + " " + uname + "\""}
                else:
                    log("Unable to find user " + assigned_user + " in Jira")
                    return {}
                
            else:
                debug("Couldn't figure out message type " + msg.get("type", "type_failed"))
            #        print("Looks like a message of type " + req["message"].get(0).get("type"))
    except Exception as inst:
        log("Try failed!")
        log(type(inst))    # the exception instance
        log(inst.args)     # arguments stored in .args
        log(inst)          # __str__ allows args to be printed directly,

    return res


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
