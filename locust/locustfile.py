import logging
import string
import random
import sys
from dataclasses import dataclass
from pathlib import Path

from locust import HttpUser, task, run_single_user, constant_throughput, constant_pacing

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)


@dataclass
class AuthData:
    grant_type: str
    client_id: str
    client_secret: str
    username: str
    password: str


@dataclass
class HostData:
    host: str
    token_url: str
    auth_data: AuthData


def get_host(url: str):
    data = url.strip("\"")
    if data.endswith(":443"):
        data = data.strip(":443")
        data = f"https://{data}"
    else:
        data = f"http://{data}"

    return data


def get_path(path: str):
    data = path.strip("\"")
    return data


def get_token_url(url: str, path: str):
    return get_host(url) + get_path(path)


def get_auth_data(indata: str):
    output = AuthData
    data = indata.split("&")

    for d in data:
        entry = d.strip("\"")
        entry = entry.split("=")
        if entry[0] == "grant_type":
            output.grant_type = entry[1]
        elif entry[0] == "client_id":
            output.client_id = entry[1]
        elif entry[0] == "client_secret":
            output.client_secret = entry[1]
        elif entry[0] == "username":
            output.username = entry[1]
        elif entry[0] == "password":
            output.password = entry[1]

    return output


def auth_data_as_dict(ad: AuthData):
    return {
        "grant_type": ad.grant_type,
        "client_id": ad.client_id,
        "client_secret": ad.client_secret,
        "username": ad.username,
        "password": ad.password
    }


def parse_csv(csv_file: Path):
    result = HostData

    logging.info(f"loading csv file {csv_file}")

    with open(csv_file) as f:
        data = f.read()
        data = data.split(",")
        result.host = get_host(data[0])
        result.token_url = get_token_url(data[1], data[2])
        result.auth_data = get_auth_data(data[3])

    return result


def parse_toml(toml_config: Path):
    import tomllib
    logging.info("loading toml configuration")
    result = HostData
    with open(toml_config) as f:
        data = f.read()
        data = tomllib.loads(data)
        result.host = get_host(data['3scale']['url'])
        result.token_url = get_token_url(data['auth']['url'], data['auth']['endpoint'])
        auth = AuthData
        auth.grant_type = data['auth']['grant_type']
        auth.client_id = data['auth']['client_id']
        auth.client_secret = data['auth']['client_secret']
        auth.username = data['auth']['username']
        auth.password = data['auth']['password']

        result.auth_data = auth

    return result


def python_version_check():
    if sys.version_info < (3, 11):
        logging.info("recommended to use python 3.11 or above and the toml configuration file")
    else:
        logging.info("recommended to use the toml configuration file format for more features")


def parse_json(json_auth: Path):
    import json
    logging.info("loading json configuration file")
    result = HostData
    with open(json_auth) as f:
        data = f.read()
        data = json.loads(data)
        result.host = data['host']
        result.token_url = get_token_url(data['sso'], data['endpoint'])
        auth = AuthData
        auth.grant_type = data['grant_type']
        auth.client_id = data['client_id']
        auth.client_secret = data['client_secret']
        auth.username = data['username']
        auth.password = data['password']

        result.auth_data = auth

    return result


def load_data():

    try:
        toml_config = Path("config.toml")
        if toml_config.is_file():
            return parse_toml(toml_config)
    except ModuleNotFoundError:
        logging.warning("module tomllib not found falling back to older configuration formats")
    python_version_check()

    json_auth = Path("auth.json")
    if json_auth.is_file():
        return parse_json(json_auth)

    auth_csv = Path("auth.csv")
    if auth_csv.is_file():
        return parse_csv(auth_csv)

    auth_csv = Path("rhsso_auth.csv")
    if auth_csv.is_file():
        return parse_csv(auth_csv)

    logging.error("no configuration file found, please create one")
    exit(1)


def generate_payload(payload_size):
    return ''.join([random.choice(string.ascii_letters) for _ in range(payload_size)])


auth_data = load_data()


class RhoamUser(HttpUser):
    host = auth_data.host
    wait_time = constant_pacing(1)
    request_headers = ""

    payload5M = generate_payload(5 * 1024 * 1024)
    payload1M = generate_payload(1024 * 1024)
    payload500K = generate_payload(500 * 1024)
    payload100K = generate_payload(100 * 1024)
    payload20K = generate_payload(20 * 1024)
    payload5K = generate_payload(5 * 1024)

    def on_start(self):
        self._create_token()

    @task(1)
    def create_token(self):
        self._create_token()

    @task(40)
    def get_data(self):
        random_id = random.randint(1, 99999)
        self.client.get(f"/nothing/{random_id}", headers=self.request_headers, name="Get Data")

    @task(11)
    def post_data_5kb(self):
        random_id = random.randint(1, 99999)
        self.client.post(f"/nothing/{random_id}",
                         json={"data": f"{self.post_data_5kb}"},
                         headers=self.request_headers, name="Post Data 5kb")

    @task(11)
    def post_data_20kb(self):
        random_id = random.randint(1, 99999)
        self.client.post(f"/nothing/{random_id}",
                         json={"data": f"{self.post_data_20kb}"},
                         headers=self.request_headers, name="Post Data 20kb")

    @task(13)
    def post_data_100kb(self):
        random_id = random.randint(1, 99999)
        self.client.post(f"/nothing/{random_id}",
                         json={"data": f"{self.post_data_100kb}"},
                         headers=self.request_headers, name="Post Data 100kb")

    @task(4)
    def post_data_500kb(self):
        random_id = random.randint(1, 99999)
        self.client.post(f"/nothing/{random_id}",
                         json={"data": f"{self.post_data_500kb}"},
                         headers=self.request_headers, name="Post Data 500kb")

    @task(2)
    def post_data_1mb(self):
        random_id = random.randint(1, 99999)
        self.client.post(f"/nothing/{random_id}",
                         json={"data": f"{self.post_data_1mb}"},
                         headers=self.request_headers, name="Post Data 1mb")

    def _create_token(self):
        with self.client.post(auth_data.token_url, auth_data_as_dict(auth_data.auth_data), name="Create Token",
                              catch_response=True) as response:
            if response.status_code >= 400:
                logging.error(response.text)
                response.failure(response.text)
            else:
                token = response.json()["access_token"]
                if token == "":
                    response.failure("empty token in response json")
                else:
                    response.success()

                self.request_headers = {
                    "authorization": "Bearer " + token
                }


if __name__ == "__main__":
    run_single_user(RhoamUser)
