from setuptools import setup
import os

def readme():
    with open(os.path.dirname(os.path.abspath(__file__)) + '/README.rst') as f:
        return f.read()

setup(
    name='jiraautomation',
    version='0.1',
    description='JIRA Simple Automation tool',
    long_description=readme(),
    url='git@github.com/Diplomat14/jiraautomation',
    author='Aleksey Denysyuk',
    author_email='diplomt@gmail.com',
    license='MIT', #TBD
    packages=['jiraautomation'],
    install_requires=[
        'pyyaml',
        'jinja2',
        'jiraorm @ git+ssh://git@github.com/Diplomat14/jiraorm.git'
        ],
    #dependency_links=['http://server/user/repo/tarball/master#egg=package-1.0'],
    entry_points = {
        'console_scripts':['jiraautomation-main=jiraautomation.console.command_line:main']
    },
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False
)