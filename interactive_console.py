#!/usr/bin/python

import pytumblr
import json
import os
import urlparse
import code
import oauth2 as oauth

def new_oauth(json_path):
    '''
    Return the consumer and oauth tokens with three-legged OAuth process and
    save in a json file in the user's home directory.
    '''

    print 'Retrieve consumer key and consumer secret from http://www.tumblr.com/oauth/apps'
    consumer_key = raw_input('Paste the consumer key here: ')
    consumer_secret = raw_input('Paste the consumer secret here: ')

    request_token_url = 'http://www.tumblr.com/oauth/request_token'
    authorize_url = 'http://www.tumblr.com/oauth/authorize'
    access_token_url = 'http://www.tumblr.com/oauth/access_token'

    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)

    # Get request token
    resp, content = client.request(request_token_url, "POST")
    request_token =  urlparse.parse_qs(content)

    # Redirect to authentication page
    print '\nPlease go here and authorize:\n%s?oauth_token=%s' % (authorize_url, request_token['oauth_token'][0])
    redirect_response = raw_input('Allow then paste the full redirect URL here:\n')

    # Retrieve oauth verifier
    url = urlparse.urlparse(redirect_response)
    query_dict = urlparse.parse_qs(url.query)
    oauth_verifier = query_dict['oauth_verifier'][0]

    # Request access token
    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'][0])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = urlparse.parse_qs(content)

    tokens = {
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'oauth_token': access_token['oauth_token'][0],
        'oauth_token_secret': access_token['oauth_token_secret'][0]
    }

    json_file = open(json_path, 'w+')
    json.dump(tokens, json_file, indent=2)
    json_file.close()

    return tokens

if __name__ == '__main__':
    json_path = os.path.expanduser('~') + '/tumblr_credentials.json'

    if not os.path.exists(json_path):
        tokens = new_oauth(json_path)
    else:
        json_file = open(json_path, "r")
        tokens = json.load(json_file)
        json_file.close()

    client = pytumblr.TumblrRestClient(
        tokens['consumer_key'],
        tokens['consumer_secret'],
        tokens['oauth_token'],
        tokens['oauth_token_secret']
    )

    print 'pytumblr client created. You may run pytumblr commands prefixed with "client".\n'

    code.interact(local=dict(globals(), **{'client': client}))
