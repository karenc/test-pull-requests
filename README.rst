=============================
README for test-pull-requests
=============================

test-pull-request is a python program written to help test pull requests on
github.  The way it works is:

1. The program polls github repositories every 15 minutes for open pull
   requests.  If the pull request is new, or the HEAD sha of the pull request
   is different, a job is pushed into the "build_queue".

2. A user written program needs to have a blocking pop operation on the
   "build_queue".  When a job comes in, run the tests and push the result into
   the "comment_queue".

3. Whenever a comment is in the "comment_queue", the program posts the comment
   to the github pull request.

Installation
------------

1. Install virtualenv

   ``sudo apt-get install python-virtualenv``

   OR

   Download it from https://pypi.python.org/pypi/virtualenv

2. Set up virtual env

   ``virtualenv .``

3. Install fabric

   ``./bin/pip install fabric``

4. Check whether paramiko is broken:

   1. Try running:

      ``./bin/fab -H localhost test``

      If you see this error "NameError: global name 'host' is not defined" then go to 4.2.

   2. Patch paramiko: (See bug https://github.com/paramiko/paramiko/pull/179)

      ``sed -i "59 s/host/socket.gethostname().split('.')[0]/" local/lib/python2.7/site-packages/paramiko/config.py``

5. Have a look at what tasks are available:

   ``./bin/fab -l``

Example usage with karenc/cnx-archive
-------------------------------------

1. Start the master (which gets the list of open pull requests from repo)

   ``./bin/fab -H localhost start_master:redis_server=localhost,repo=karenc/cnx-archive``

2. Start the build worker (which set up the environment and runs the tests)

   ``./bin/python run_tests.py archive localhost -n raring-clean-clone -i 192.168.122.101`` (inside karenc/connexions-setup)

3. Start the comment worker (which posts comments to the pull requests)

   ``./bin/fab -H localhost start_comment_worker:redis_server=localhost``
