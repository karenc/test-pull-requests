from setuptools import setup, find_packages

setup(
        name='test_pull_requests',
        version='0.0',
        author='karen chan',
        author_email='karen@karen-chan.com',
        url='https://github.com/karenc/test-pull-requests',
        packages=find_packages(),
        install_requires=(
            'redis',
            ),
        include_package_data=True,
        entry_points={
            'console_scripts': [
                'test-pull-requests-master = test_pull_requests.scripts:master',
                'test-pull-requests-comment-worker = test_pull_requests.scripts:comment_worker',
                ],
            },
        )
