from fastapi import FastAPI
from pydantic import BaseModel

LeanIPGrid = FastAPI()

@LeanIPGrid.get("/")
async def root():
    return {"message": "Hellow WorlD!"}


@LeanIPGrid.get("/cidr/{cidr}")
async def get_cidr(cidr):
    return {"cidr": cidr}

@LeanIPGrid.get("/network/{network}")
async def get_specific_network(network):
    return {"network": network}

@LeanIPGrid.get("/networks")
async def list_networks():
    return {"message": "list of all network"}

@LeanIPGrid.get("/node/{node}")
async def get_cidr(cidr):
    return {"cidr": cidr}

class Node(BaseModel):
    name: str
    description: str = None
    key: str
    ip: str

@LeanIPGrid.post("/node/{node}")
async def get_cidr(cidr):
    return {"cidr": cidr}

@LeanIPGrid.get("/nodes")
async def get_cidr(cidr):
    return {"cidr": cidr}


