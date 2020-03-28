from setuptools import setup


tests_require = [
    'pytest',
    'pytest-aiohttp',
    'aioresponses',
]

setup(
    name='local_proxy',
    version='1.0.0.dev',
    author='primetech',
    author_email='mathias@primtech.dev',
    packages=['local_proxy', ],
    url='http://pypi.python.org/pypi/local_proxy/',
    license='GPL',
    description='Cache endpoint localy (filestorage)',
    long_description=open('README.txt').read(),
    install_requires=[
        'aiohttp',
        'gunicorn',
        'diskcache',
    ],
    tests_require=tests_require,
    setup_requires=['pytest-runner', ],
    extras_require={
        'tests': tests_require,
    },
)
