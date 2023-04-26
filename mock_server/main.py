from fastapi import FastAPI, Body, Depends, Form
from pydantic import BaseModel

app = FastAPI()


class Payload(BaseModel):
    data: str


class AuthData(BaseModel):
    grant_type: str
    client_id: str
    client_secret: str
    username: str
    password: str


@app.get("/nothing/get/{name}")
@app.get("/nothing/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/nothing/{name}")
async def say_hello(name: str, payload: Payload):
    return {"message": f"Hello {name}", "payload": payload}


@app.post("/auth/realms/protocol/openid-connect/token")
def get_token(grant_type: str = Form(),
              client_id: str = Form(),
              client_secret: str = Form(),
              username: str = Form(),
              password: str = Form(),
              ):
    return {"access_token": "abc123"}
