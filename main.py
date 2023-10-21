from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import uuid

LeanIPGrid = FastAPI()

con = sqlite3.connect("leanipgrid.db")

cursor = con.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS nodes(uuid,name,ip,key,url,description,node)")

cursor = con.cursor()

cursor.execute("SELECT * FROM nodes WHERE node = 'this'")

this = cursor.fetchone()

def decimal_to_binary(input):
#this function exists to transmute the cidrs into various notation systems and return it. It is helpfull to make a computation in various sub functions later on

    if "/" in input:
        decimal = input.split('/')
        octets = decimal[0].split('.')
        if len(decimal[1]) == 2:
            bit_netmask = decimal[1]
            binary_netmask = ''
        else:
            netmask_octets = decimal[1].split('.')
            binary_netmask = [bin(int(octet)).lstrip('0b').zfill(8) for octet in netmask_octets]
            binary_netmask = ''.join(binary_netmask)
            bit_netmask = binary_netmask.count('1')
    else:
        octets = input.split(".")
        bit_netmask = 32
        binary_netmask = '11111111111111111111111111111111'

    binary_octets = [bin(int(octet)).lstrip('0b').zfill(8) for octet in octets]
    binary_ip = ''.join(binary_octets)        

    result = {"ip": {"binary": binary_ip, "decimal": ""}, "netmask": {"binary": binary_netmask, "decimal": "", "bits": bit_netmask}}

    return {"binary_ip": binary_ip, "netmask_bits": bit_netmask, "binary_netmask": binary_netmask}

@LeanIPGrid.get("/")
async def root():
    return {"message": "Hellow WorlD!"}

@LeanIPGrid.get("/me")
async def me():

    cursor = con.cursor()
    res = cursor.execute("SELECT * FROM nodes WHERE uuid = '" + this[uuid] + "'")

    result = res.fetchone()

    return {result}





@LeanIPGrid.get("/v1/cidr/{cidr:path}")
# get data about specific IP (with netmask)
async def get_cidr(cidr: str):

    result = decimal_to_binary(cidr)

    return {"binary_ip": result}






@LeanIPGrid.get("/v1/ipv4/network/{network_address}")
#will present all the information related to specific network based on network address
async def get_specific_network(network):

#Get the current data about all the fields in a table - POSSIBLY CAN BE MOVED TO INDEPENDANT FUNCTION AND REUSED ELSEWHERE
    cursor = con.cursor()
    cursor.execute("PRAGMA table_info(ipv4_networks)")
    column_name = [column[1] for column in cursor.fetchall()]

    network_address = network.split("/")

 #   return {"network": network_address}

    cursor.execute("SELECT * FROM ipv4_networks WHERE network_address = '" + network_address[0] +"'")
    result = cursor.fetchone()

    return {"network": result}


@LeanIPGrid.get("/v1/ipv4/network/{node_uuid}")
#list all the networks which are managed by a defined node (expressed by UUID)
async def get_specific_network(uuid):
#    return {"network": network}

#    uuid = network
    
    cursor = con.cursor()
    cursor.execute("PRAGMA table_info(ipv4_networks)")
    column_name =  [column[1] for column in cursor.fetchall()]

#we're getting all the data from nodes table    
    cursor.execute("SELECT * FROM ipv4_networks WHERE node_uuid = '" + uuid + "';")
    
    results = cursor.fetchall()

#create an output which will follow key:value where the key is the name of a column and a data are relative data from all rows.
    result = []
    for row in results:
        row_dict = {}
        for i in range(len(column_name)):
            row_dict[column_name[i]] = row[i]
        result.append(row_dict)
#    print(result) 
    
    return result


@LeanIPGrid.get("/v1/ipv4/networks")
# list all networks defined
async def list_networks():
#To make it dynamic (if new column will be added) we have to first get all the column names
    cursor = con.cursor()
    cursor.execute("PRAGMA table_info(ipv4_networks)")
    column_name =  [column[1] for column in cursor.fetchall()]

#we're getting all the data from nodes table    
    cursor.execute("SELECT * FROM ipv4_networks")
    
    results = cursor.fetchall()

#create an output which will follow key:value where the key is the name of a column and a data are relative data from all rows.
    result = []
    for row in results:
        row_dict = {}
        for i in range(len(column_name)):
            row_dict[column_name[i]] = row[i]
        result.append(row_dict)
    
    return result



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


