from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import uuid

LeanIPGrid = FastAPI()

con = sqlite3.connect("leanipgrid.db")

cursor = con.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS nodes(uuid,name,ip,key,url,description)")

@LeanIPGrid.get("/")
async def root():
    return {"message": "Hellow WorlD!"}


@LeanIPGrid.get("/v1/cidr/{cidr}")
async def get_cidr(cidr):
    return {"cidr": cidr}

@LeanIPGrid.get("/v1/ipv4/network/{network}")
async def get_specific_network(network):
    return {"network": network}

@LeanIPGrid.get("/v1/ipv4/networks")
async def list_networks():
    query = 'SELECT * FROM ipv4_networks'
    res = con.execute(query)
    return res.fetchall()
##    return {"message": "list of all network"}
    
@LeanIPGrid.get("/v1/node/{node}")
async def get_cidr(cidr):
    return {"cidr": cidr}

class Node(BaseModel):
    name: str
    description: str = None
    key: str
    ip: str
    url: str
    master_key: str

@LeanIPGrid.post("/v1/node/")
async def add_node(node: Node):
    return node

@LeanIPGrid.get("/v1/nodes")
# list all of the nodes with all the information related.
async def get_all_nodes():

#To make it dynamic (if new column will be added) we have to first get all the column names
    cursor = con.cursor()
    cursor.execute("PRAGMA table_info(nodes)")
    column_name =  [column[1] for column in cursor.fetchall()]

#we're getting all the data from nodes table    
    cursor.execute("SELECT * FROM nodes")
    
    results = cursor.fetchall()

#create an output which will follow key:value where the key is the name of a column and a data are relative data from all rows.
    result = []
    for row in results:
        row_dict = {}
        for i in range(len(column_name)):
            row_dict[column_name[i]] = row[i]
        result.append(row_dict)
    
    return result
#    return {"cidr": cidr}


