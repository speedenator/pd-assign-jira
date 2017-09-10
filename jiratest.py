#!/usr/bin/env python

from jira import JIRA
from jira.exceptions import JIRAError

options = {
    'server': 'https://cookbrite.atlassian.net'
}

# ZOMG
try:
    jira = JIRA(options, basic_auth = ('erik@metabrite.com', '2069151472'))
except JIRAError as e:
    if e.status_code == 401:
        print "Login to JIRA failed. Check your username and password"
        exit(-1)

email = 'erik@metabrite.com'

incident_key = 'OPS-7'

users = jira.search_users(email)

print "Users: " + str(len(users))
for u in users:
    print users

if len(users):
    print "At least one user, using first"

    u = users[0]
    uname = u.name
    print "User name: " + uname
    
    
