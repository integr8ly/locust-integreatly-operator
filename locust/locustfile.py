import logging
import string
import random
from dataclasses import dataclass

from locust import HttpUser, task, run_single_user, constant_throughput, constant_pacing


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


def parse_csv():
    result = HostData
    with open("rhsso_auth.csv") as f:
        data = f.read()
        data = data.split(",")
        result.host = get_host(data[0])
        result.token_url = get_token_url(data[1], data[2])
        result.auth_data = get_auth_data(data[3])

    return result


def generate_payload(payload_size):
    return ''.join([random.choice(string.ascii_letters) for _ in range(payload_size)])


auth_data = parse_csv()


class RhoamUser(HttpUser):
    host = auth_data.host
    wait_time = constant_pacing(9.25)
    request_headers = ""

    payload5M = generate_payload(5 * 1024 * 1024)
    payload1M = generate_payload(1024 * 1024)
    payload500K = generate_payload(500 * 1024)
    payload100K = generate_payload(100 * 1024)
    payload20K = generate_payload(20 * 1024)
    payload5K = generate_payload(5 * 1024)

    def on_start(self):
        print(auth_data)
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
