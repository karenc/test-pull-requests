import time

from fabric.api import *
import fabric.contrib.files

env.use_ssh_config = True

def _setup():
    sudo('apt-get install --yes python-setuptools python-virtualenv')

def setup_redis():
    sudo('apt-get install --yes redis-server')
    fabric.contrib.files.comment('/etc/redis/redis.conf', '^bind .*',
            use_sudo=True)
    sudo('/etc/init.d/redis-server restart')

def _update_repo():
    run('git remote update -p')
    run('git reset --hard origin/master')

def start_master(redis_server, repo):
    """Arguments: redis_server (e.g. 192.168.0.2) and repo (e.g. karenc/test-pull-requests)
    """
    _setup()
    if not fabric.contrib.files.exists('test-pull-requests'):
        run('git clone https://github.com/karenc/test-pull-requests')
    with cd('test-pull-requests'):
        _update_repo()
        if not fabric.contrib.files.exists('bin'):
            run('virtualenv .')
        run('./bin/python setup.py install')
        while True:
            run('./bin/test-pull-requests-master {} {}'.format(redis_server, repo))
            time.sleep(15 * 60)

def start_comment_worker(redis_server):
    """Arguments: redis_server (e.g. 192.168.0.2)
    """
    _setup()
    if not fabric.contrib.files.exists('test-pull-requests'):
        run('git clone https://github.com/karenc/test-pull-requests.git')
    with cd('test-pull-requests'):
        _update_repo()
        if not fabric.contrib.files.exists('bin'):
            run('virtualenv .')
        run('./bin/python setup.py install')
        run('./bin/test-pull-requests-comment-worker {}'.format(redis_server))

def test():
    run('uname -a')
