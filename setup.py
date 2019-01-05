"""
NYPR Whats_on metadata microservice
"""
from setuptools import setup

setup(
    author='NYPR Digital',
    author_email='digitalops@nypublicradio.org',
    dependency_links=[
        'https://github.com/nypublicradio/nyprsetuptools/tarball/master#egg=nyprsetuptools-0.0.0'
    ],
    description=__doc__,
    entry_points={
        'distutils.commands': [
            'requirements = nyprsetuptools:InstallRequirements',
            'test = nyprsetuptools:PyTest',
            'test_requirements = nyprsetuptools:InstallTestRequirements',
            'deploy = nyprsetuptools:LambdaDeploy',
        ],
        'distutils.setup_keywords': [
            'requirements = nyprsetuptools:setup_keywords',
            'test = nyprsetuptools:setup_keywords',
            'test_requirements = nyprsetuptools:setup_keywords',
            'deploy = nyprsetuptools:setup_keywords',
        ],
    },
    install_requires=[
        'raven',
        'redis',
        'xmltodict',
    ],
    license='BSD',
    long_description=__doc__,
    name='whats-on-microservice',
    package_data={},
    packages=['whatsonms'],
    scripts=[],
    setup_requires=[
        'nyprsetuptools>=0.0.0'
    ],
    tests_require=[
        'mockredispy',
        'pytest>=3.0.6',
        'pytest-cov',
        'pytest-env',
        'pytest-flake8',
        'pytest-mock',
        'pytest-sugar',
    ],
    url='https://github.com/nypublicradio/whats_on_microservice',
    version='0.0.0',
    zip_safe=False,
)
