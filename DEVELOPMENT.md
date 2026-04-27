# nefila | Development

## Setup

pipenv install --dev
pipenv update

## Test Setup

- Test suite use the following values by default:

    FORTIGATE_HOSTNAME: 192.168.0.30
    NEFILA_USERNAME: nefila-admin
    NEFILA_PASSWORD: nefila-password
    NEFILA_TOKEN: <blank>

You can override any of those values using environment variables:

    export FORTIGATE_HOSTNAME=10.20.10.11
    export NEFILA_USERNAME=admin
    export NEFILA_PASSWORD=fortinet
    export NEFILA_TOKEN=''

## Tests

Run tests

    pytest tests/test_fortigate.py

Run tests with output

    pytest tests/test_fortigate.py -s -v

Coverage report

    # check results at htmlcov/index.html
    pytest --cov-report html tests/test_fortigate.py --cov=./nefila/    

    pytest --cov-report term-missing --cov=nefila tests/
    pytest --cov-report term-missing --cov=nefila tests/ -k tests/test_fortiswitch
    pytest --cov-report term-missing --cov=nefila tests/ -k fortigate --junitxml test_fortigate.xml
    pytest --cov-report term-missing --cov=nefila tests/ -k fortigate --junitxml test_fortigate.xml --junit_family=xunit2 --capture=no --verbose
    pytest ./tests/test_fortigate.py::test_login_live -s -v --junitxml test_fortigate.xml --junit_family=xunit2

Specific test

    pytest tests/test_fortigate.py::test_system_interface -s

## Publish on PyPI

- Change version on setup.py
- Commit and tag on github


    git add *
    git commit -am 'updated csrf code to support 7.4'
    git tag -a v0.0.5 -m 'updated csrf code to support 7.4'
    git push --tags

- Create release on github

- Create package and push to PyPI

    python setup.py sdist
    twine upload dist/*

- Test and check version

    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install --upgrade pip
    pip install wheel
    pip install nefila
    pip list
