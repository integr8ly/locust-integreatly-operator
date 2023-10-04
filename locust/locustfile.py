import logging
import string
import random
import sys
from dataclasses import dataclass
from pathlib import Path

from locust import HttpUser, task, run_single_user, constant_throughput, constant_pacing

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

@dataclass
class HostData:
    host: str
    token_url: str


def get_host(url: str):
    data = url.strip("\"")
    if data.endswith(":443"):
        data = data.strip(":443")
        data = f"{data}"
    else:
        data = f"{data}"

    return data


def get_path(path: str):
    data = path.strip("\"")
    return data

def parse_csv(csv_file: Path):
    result = HostData

    logging.info(f"loading csv file {csv_file}")

    with open(csv_file) as f:
        data = f.read()
        data = data.split(",")
        result.host = get_host(data[0])
        result.param = data[1]

    return result


def parse_toml(toml_config: Path):
    import tomllib
    logging.info("loading toml configuration")
    result = HostData
    with open(toml_config) as f:
        data = f.read()
        data = tomllib.loads(data)
        result.host = get_host(data['3scale']['url'])
        result.param = data['3scale']['param']

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
        result.host = get_host(data['host'])
        result.param = data['param']

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
    param = auth_data.param
    wait_time = constant_pacing(1)
    request_headers = ""

    payload5M = generate_payload(5 * 1024 * 1024)
    payload1M = generate_payload(1024 * 1024)
    payload500K = generate_payload(500 * 1024)
    payload100K = generate_payload(100 * 1024)
    payload20K = generate_payload(20 * 1024)
    payload5K = generate_payload(5 * 1024)

    @task(40)
    def get_data(self):
        random_id = random.randint(1, 99999)
        self.client.get(f"/nothing/{random_id}/{self.param}", headers=self.request_headers, name="Get Data")

    @task(11)
    def post_data_5kb(self):
        random_id = random.randint(1, 99999)
        self.client.post(f"/nothing/{random_id}/{self.param}",
                         json={"data": f"{self.post_data_5kb}"},
                         headers=self.request_headers, name="Post Data 5kb")

    @task(11)
    def post_data_20kb(self):
        random_id = random.randint(1, 99999)
        self.client.post(f"/nothing/{random_id}/{self.param}",
                         json={"data": f"{self.post_data_20kb}"},
                         headers=self.request_headers, name="Post Data 20kb")

    @task(13)
    def post_data_100kb(self):
        random_id = random.randint(1, 99999)
        self.client.post(f"/nothing/{random_id}/{self.param}",
                         json={"data": f"{self.post_data_100kb}"},
                         headers=self.request_headers, name="Post Data 100kb")

    @task(4)
    def post_data_500kb(self):
        random_id = random.randint(1, 99999)
        self.client.post(f"/nothing/{random_id}/{self.param}",
                         json={"data": f"{self.post_data_500kb}"},
                         headers=self.request_headers, name="Post Data 500kb")

    @task(2)
    def post_data_1mb(self):
        random_id = random.randint(1, 99999)
        self.client.post(f"/nothing/{random_id}/{self.param}",
                         json={"data": f"{self.post_data_1mb}"},
                         headers=self.request_headers, name="Post Data 1mb")


if __name__ == "__main__":
    run_single_user(RhoamUser)
