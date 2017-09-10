# PD2Jira - sample webhook implementation in Python

This is a really simple webhook implementation that gets PagerDuty
webhooks, looks for incident.acknowledge, and then assigns an
appropriate Jira task. Assumes using Jira OnDemand.

Requires the following config:
USER - a Jira OnDemand user
PASS - password for user. Yeah, this sucks.
SITE - your on-demand site (e.g. https://SITE.atlassian.net --- but
just the SITE part)

# Workflow

If you use PagerDuty for pages, and use Jira to track the issues, this
is for you.

This assumes the following workflow (and setup):

1. Something happens
2. A Jira issue is created
3. Jira uses a webhook to create a PagerDuty incident

A problem with the above is that once the on-call responds (and there
may be escalations / shadow / etc.), the Jira issue is still
unassigned or set to a default person, as opposed to whomever is now
on the ticket. This requires the person ACKing the issue to find the
Jira issue and then assign it to themselves, which is a bit of a pain.

This heroku web app requires an additional PagerDuty webhook, which will
be called after any PagerDuty incident is touched. It will look for
acknowledgements, and then call the Jira API assign the issue in the
page to the user acknowledging. It assumes the emails in PagerDuty and
Jira are the same (but usernames in Jira can and usually are different).

# Setup

We assume you already have the Jira -> PagerDuty Web Hook set up. If
not, go here: [https://www.pagerduty.com/docs/guides/jira-webhook-email-integration-guide/][https://www.pagerduty.com/docs/guides/jira-webhook-email-integration-guide/]

First, clone or fork this repo:

% git clone https://github.com/speedenator/pd2jira.git
% cd pd2jira

## Deploy this to Heroku

(see
[https://devcenter.heroku.com/articles/getting-started-with-python#deploy-the-app][Heroku
Python docs] for more details)

% heroku create

We'll assume the app name here is 'hooky-mchookface-1234'. Now, set
some config vars:

% heroku config:set USER=<jira username>
% heroku config:set PASS=<jira password>
% heroku config:set SITE=<jira site>

To be clear, let's say your site is 'https://spaceballs.atlassian.net',
your name is 'skroob@spaceballs.com', and your password is '12345'.

% heroku config:set USER=skroob@spaceballs.com
% heroku config:set PASS=12345
% heroku config:set SITE=spaceballs

Note: given how crappy putting a password in a config is, I'd
recommend you make a special Jira user for this vs a real one.

Now, push the code:

% git push heroku master

Make sure things are working via:

% heroku logs --tail

(need more info? turn on verbose logging:)

##  Setup PagerDuty Web Hook

Go to the Service you want to use (have lots of services? Do this for
each. Have lots and lots of services? This will suck.)

Click on "Integrations" and then "Add New Extension." Create a Generic
Webhook, name it 'pd2jira' (or whatever), and use this as the URL:

`https://hooky-mchookface-1234.herokuapp.com/webhook`

(replacing hooky-mchookface-1234 with whatever Heroku gave you)

## Test it

Finally, test it out. Create a Jira issue, make sure it made a page,
and then see that the WebApp did its thing!

Note: you HAVE to have Jira make the PagerDuty incidents. If you just
create new ones, there will be no Jira issue key for pd2jira to work.

# Deploy to:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## How to make contributions?
Send me a PR.

## License
See [LICENSE](LICENSE).

