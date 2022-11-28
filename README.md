# locust integreatly operator

This repo contains code to do load testing on the integreatly-operator.

 A `rhsso_auth.csv` file is required to be in the same location as the locustfile.
 This file is currently create by the hyperfoil load testing function.
 
## Run load test with remote host
Log into a remote instances and insure the following tooling is installed
```shell
sudo dnf install python39 -y
pip3 install locust
mkdir locust
```

From the local machine copy the source files.
```shell
scp -i ~/.ssh/some_key.pem -r locust/* ec2-user@<remote.url>:locust
```

After an initial hyperfoil run copy the `rhsso_auth.csv` file from `/tmp/hyperfoil/runs/****/`.

Start locust and the max number of workers supported by the ec2 instances.
```shell
~/locust/start.sh
```

Navigate to the locust UI via http://<remote.url>:8089.
Here you can start the load testing.

After the test have run and test results downloaded, locust can be stopped using `~/locust/kill.sh`

## Develop load test locally
Set up the local environment using poetry.
```shell
poetry install
```

If you are wishing not to use the mock server you can set up the environment using.
```shell
poetry install --no-dev
```

As the `rhsso_auth.csv` file is required there is a sample file that will work with the mock server.
```shell
cp locust/sample.rhsso_auth.csv locust/rhsso_auth.csv
```

Active the mock server if needed.
```shell
poetry run uvicorn --reload mock_server.main:app
```

Start an instance of locust.
```shell
cd locust
poetry run locust
```

## Usefully Resources
* [doc.locust.io](https://docs.locust.io/en/stable/)
* [3scale-qe/3scale-test](https://github.com/3scale-qe/3scale-tests)
* [integr8ly/integreatly-operator](https://github.com/integr8ly/integreatly-operator)