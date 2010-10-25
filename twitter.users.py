# -*- coding: utf-8 -*-

import sys
import pg
import httplib
import simplejson
import datetime
import oauth2 as oauth
import pprint

pgconn = pg.DB('YOUR_DB', '127.0.0.1', 5432, None, None, 'YOUR_USERNAME', 'YOUR_PASSWORD')
table_name = "twitter_users"

no_overwrite = False
is_oauth = True
if len(sys.argv) > 1:
    user_id = sys.argv[1]
    if len(sys.argv) > 2:
	for i in range(2,len(sys.argv)):
	    if sys.argv[i] == "-no" or sys.argv[i] == "--no-overwrite":
		no_overwrite = True
	    if sys.argv[i] == "-o" or sys.argv[i] == "--oauth":
		is_oauth = True
	    if sys.argv[i] == "-na" or sys.argv[i] == "--no-auth":
		is_oauth = False
else:
    print "user_id missing"
    sys.exit()

try:
    user_id = str(int(user_id))
except (ValueError):
    print "argument invalid: given " + user_id
    sys.exit()

if user_id > 0:
    conn = httplib.HTTPConnection("api.twitter.com")
    ok = False
    if is_oauth:
	consumer_key = "YOUR_KEY"
	consumer_secret = "YOUR_SECRET"
	oauth_token = "YOUR_TOKEN"
	oauth_token_secret = "YOUR_TOKEN_SECRET"
	consumer = oauth.Consumer(key = consumer_key, secret = consumer_secret)
	token = oauth.Token(key = oauth_token, secret = oauth_token_secret)
	client = oauth.Client(consumer, token)
	resp, content = client.request("http://api.twitter.com/1/users/show.json?user_id=" + user_id, "GET")
	r = content
	if len(r) > 2:
	    ok = True
	    j = simplejson.loads(r)
    else:
	try:
	    conn.request("GET", "/1/users/show.json?user_id=" + user_id)
	except (Exception):
	    sys.exit(sys.exc_info())
	r = conn.getresponse()
	if r.status == 200:
	    ok = True
	    j = simplejson.load(r)
    if ok:
	l = j
    	r = {"id": l["id"], "name": l["name"].encode("utf8"), "screen_name": l["screen_name"].encode("utf8"),
	"description": l["description"].encode("utf8"), "profile_image_url": l["profile_image_url"].encode("utf8"),
	"url": l["url"].encode("utf8"), "followers_count": l["followers_count"],
	"utc_offset": l["utc_offset"], "time_zone": l["time_zone"], "profile_background_image_url": l["profile_background_image_url"].encode("utf8"),
	"friends_count": l["friends_count"],"created_at": l["created_at"], "favourites_count": l["favourites_count"],
	"notifications": l["notifications"],"geo_enabled": l["geo_enabled"],
	"verified": l["verified"], "statuses_count": l["statuses_count"], "lang": l["lang"],
	"contributors_enabled": l["contributors_enabled"], "follow_request_sent": l["follow_request_sent"],
	"listed_count": l["listed_count"], "show_all_inline_media": l["show_all_inline_media"],
	"retrieved": "NOW()"}
	try:
	    pgconn.insert(table_name, r)
	except pg.ProgrammingError, pg.InternalError:
	    print "user duplicate found in DB... trying to update instead"
	    try:
		pgconn.update(table_name, r)
	    except:
		print "an error has occurred (row cannot be updated)"
	    print r
    else:
	print "Error: " + r