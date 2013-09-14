import argparse
import base64
import getpass
import json
import shutil
import subprocess
import tempfile
import urllib2

import redis

PULL_REQUESTS_URL = 'https://api.github.com/repos/{repo}/pulls'
ADD_COMMENT_URL = 'https://api.github.com/repos/{repo}/issues/{id}/comments'

def _get_pull_requests(repo):
    pull_requests = urllib2.urlopen(PULL_REQUESTS_URL.format(repo=repo)).read()
    pull_requests = json.loads(pull_requests)
    results = []
    for pull_request in pull_requests:
        yield {
            'id': pull_request['number'],
            'sha': pull_request['head']['sha'],
            'clone_url': pull_request['head']['repo']['clone_url'],
            }

def master():
    parser = argparse.ArgumentParser(description='Test pull requests master')
    parser.add_argument('redis_server', help='e.g. localhost')
    parser.add_argument('repo', help='e.g. karenc/test-pull-requests')

    args = parser.parse_args()
    print 'start master: {}'.format(args)

    server = redis.Redis(args.redis_server)
    for pull_request in _get_pull_requests(args.repo):
        key = '{}/{}'.format(args.repo, pull_request['id'])
        last_sha = server.get(key)
        if last_sha != pull_request['sha']:
            server.set(key, pull_request['sha'])
            server.rpush('build_queue', json.dumps({
                'repo': args.repo,
                'clone_url': pull_request['clone_url'],
                'sha': pull_request['sha'],
                'pull_request_id': pull_request['id'],
                }))

def comment_worker():
    parser = argparse.ArgumentParser()
    parser.add_argument('redis_server', help='e.g. localhost')

    args = parser.parse_args()
    print 'start comment worker: {}'.format(args)
    username = raw_input('git username: ')
    password = getpass.getpass('git password: ')

    headers = [
            ('Authorization', 'Basic %s' % base64.urlsafe_b64encode(
                ':'.join([username, password]))),
            ('Content-Type', 'application/json'),
            ('Accept', 'application/json'),
            ]

    server = redis.Redis(args.redis_server)
    while True:
        pull_request = json.loads(server.blpop('comment_queue')[1])
        url = ADD_COMMENT_URL.format(
            repo=pull_request['repo'],
            id=pull_request['pull_request_id'])

        req = urllib2.Request(url)
        for header in headers:
            req.add_header(*header)
        urllib2.urlopen(req, json.dumps({
            'body': pull_request['test_results']}))
