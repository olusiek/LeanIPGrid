from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import uuid
import logging

LeanIPGrid = FastAPI()
logging.basicConfig(level=logging.INFO)

con = sqlite3.connect("leanipgrid.db")

cursor = con.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS nodes(uuid,name,ip,key,url,description,node)")

cursor = con.cursor()

cursor.execute("SELECT * FROM nodes WHERE node = 'this'")

this = cursor.fetchone()

def bin2dec(binary_mask):
#this function makes a transformation of binary IPv4 notation into decimal one (for both ip and subnet mask)
    result = ''
    octets = [binary_mask[i:i+8] for i in range(0, len(binary_mask), 8)]
    decimal_octets = [int(octet, 2) for octet in octets]
    result = '.'.join(map(str, decimal_octets))

    return result

def dec2bin(input):
#This function makes a tranformation from decimal IP/netmask into binary expression
    octets = input.split('.')
    result = [bin(int(octet)).lstrip('0b').zfill(8) for octet in octets]
    result = ''.join(result)

    return result

def ipv4_bin2bit(input):

    result = input.find('0')

    return result

def ipv4_bit2bin(input):

    result = ''
    result = result.ljust(int(input),"1")
    result = result.ljust(32,'0')

    return result

def ipv4_bcast_address(network_address_binary, subnet_mask_binary):
    # logical AND between network address and subnet mask
    network_address = int(network_address_binary, 2)
    subnet_mask = int(subnet_mask_binary, 2)
    network = network_address & subnet_mask

    # Logical NOT on subnet netmask
    inverted_subnet_mask = ~subnet_mask & 0xFFFFFFFF  # Zastosowanie maski 32-bitowej

    # Logical OR between logical NOT below and network address
    broadcast = network | inverted_subnet_mask

    # changing the format into binary
    broadcast_binary = format(broadcast, '032b')

    return broadcast_binary


def ipv4_network_address():
#This function will calculate network address of a cidr

    return result

def decimal_to_binary(input):
#this function exists to transmute the cidrs into various notation systems and return it. It is helpfull to make a computation in various sub functions later on

    binary_ip = ''
    decimal_ip = ''
    binary_netmask = ''
    decimal_netmask = ''
    bit_netmask = ''
    result = "abc"

    if "/" in input:
        #if there a / it means it is not a /32. it can be either /24 in bit notation or 255.255.255.255 in decimal
        decimal = input.split('/')
        decimal_ip = decimal[0]
        binary_ip = dec2bin(decimal_ip)

        if len(decimal[1]) > 2:
            decimal_netmask = decimal[1]
            binary_netmask = dec2bin(decimal_netmask)
            bit_netmask = ipv4_bin2bit(binary_netmask)

        else:
            bit_netmask = decimal[1]
            binary_netmask = ipv4_bit2bin(bit_netmask)
#            binary_netmask = binary_netmask.ljust(int(bit_netmask),'1')
            decimal_netmask = bin2dec(binary_netmask)
    else:
        #if there's no / we assume it is a host address (/32)
        decimal_ip = input
        binary_ip = dec2bin(input)
        bit_netmask = '32'
        binary_netmask = binary_netmask.ljust(int(bit_netmask),'1')
        decimal_netmask = bin2dec(binary_netmask)

    result = {"ip": {"binary": binary_ip, "decimal": decimal_ip}, "netmask": {"binary": binary_netmask, "decimal": decimal_netmask, "bits": bit_netmask}}
    return result
        
def ipv4_network_finder(cidr: str,netmask: str):
#this function is created to find a matching network_address based on IP and netmask given. It will invoke itself if needed.
#if the network_address is not defined, the netmask will be changed by changing last 1 with 0. This loop occurs untill there's a proper 
# network address found in local database. The answer can be:
# - locally defined network (then the answer consists GLOBAL and LOCAL params)
# - network defined in another node (the answer consists of url of another node and global parameters available)
# this function must be invoked with binary expresion on input for both parameters.

    if len(cidr) != 32 or not all(bit in '01' for bit in cidr):
#        print('invalid cidr')
        return 

    if len(netmask) != 32 or not all(bit in '01' for bit in netmask):
#        print('invalid netmask')
        return
    
    network_address = ''.join(str(int(bit_ip) & int(bit_mask)) for bit_ip, bit_mask in zip(cidr, netmask))
#    print("Network address: " + network_address)

    first_zero = netmask.find('0')
#    print(first_zero)
    if first_zero == 0:
        print("skonczylem przeszukiwanie, brak wynikow")
        return

    cursor = con.cursor()
    querry = "SELECT * FROM ipv4_networks WHERE network_address_binary = '" + network_address + "' AND subnet_mask_binary = '" + netmask + "'"
#    if debug == 1:
#        print(querry)
    
    cursor.execute(querry)

    result = cursor.fetchone()

    if result == None:
        new_zero = netmask.find('0') - 1
        network_portion = str('1') * new_zero
#        print(network_portion)
#        print(netmask)
        netmask = network_portion.ljust(32,'0')

        result = ipv4_network_finder(cidr,netmask)
    else: 
        print("----------------------------------")
        print(result)
        print("----------------------------------")

#        print("ZNALAZLEM DOPASOWANIE: " + result["network_address"])

#        netmask_dec = bin2dec(netmask)
#        print("decimal value: " + netmask_dec)

    print(type(result))
    return result



@LeanIPGrid.get("/")
async def root():
    return {"message": "Hellow WorlD!"}

@LeanIPGrid.get("/me")
async def me():

#To make it dynamic (if new column will be added) we have to first get all the column names
    cursor = con.cursor()
    cursor.execute("PRAGMA table_info(nodes)")
    column_name =  [column[1] for column in cursor.fetchall()]
#    logging.info(column_name)
#we're getting all the data from nodes table    
    cursor.execute("SELECT * FROM nodes where node = 'this'")
    
    results = cursor.fetchall()

#create an output which will follow key:value where the key is the name of a column and a data are relative data from all rows.
    result = []
    for row in results:
        row_dict = {}
        for i in range(len(column_name)):
            row_dict[column_name[i]] = row[i]
        result.append(row_dict)
#    logging.info(result)
#   logging.info(result[0]['ip'])
    return result

@LeanIPGrid.get("/v1/cidr/{cidr:path}")
# get data about specific IP (with netmask)
async def get_cidr(cidr: str):

    result = decimal_to_binary(cidr)

    return {"result": result}


@LeanIPGrid.get("/v1/ipv4/network/{network_address}")
# will present all the information related to specific network based on network address. 
# if the network adress is not managed locally, it will return global params and node who is managing (url)
# if managed locally both global and local params will be returned.

async def get_specific_network(network):

    result = 1
    network_address = network.split("/")

# first we have to check what notation is being used. to do so we're assuming 
# for network portion:
# if len == 32 and consists only 0 and 1 ->binary format (do nothing)
# if len between 7 and 15 and consists only numbers and 3 dots - decimal format (convert to binary)
# else return erros
# for netmask:
# if is a number between 0 and 32 - bits notation (must be converted to binary)
# if len == 32 and consists only 0 and 1 - binary format (do nothing)
# if len between 7 and 15 and consists only numners and 3 dots - decimal format (convert to binary)
    if len(network_address[0]) == 32:
        cidr = network_address[0] 
    elif 7 <= len(network_address[0]) <= 15:
        cidr =  dec2bin(network_address[0])
    else:
        return {"ERROR WRONG SUBNET MASK"}

    if len(network_address[1]) == 32:
        netmask = network_address[1] 
    elif 7 <= len(network_address[1]) <= 15:
        netmask =  dec2bin(network_address[1])
    elif 1 <= len(network_address[1]) <= 2:
        netmask = ipv4_bit2bin(network_address[1])
    elif network_address[1] == None:
        netmask = ipv4_bit2bin(32)
    else:
        return {"ERROR WRONG SUBNET MASK"}
    
    logging.info(cidr)
    logging.info(netmask)
    result = ipv4_network_finder(cidr,netmask)
    logging.info(result)
    
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


#LeanIPGrid.get
@LeanIPGrid.get("/v1/node/{node}")
async def get_cidr(uuid):

#To make it dynamic (if new column will be added) we have to first get all the column names
    cursor = con.cursor()
    cursor.execute("PRAGMA table_info(nodes)")
    column_name =  [column[1] for column in cursor.fetchall()]

#we're getting all the data from nodes table    
    cursor.execute("SELECT * FROM nodes where uuid = '" + uuid + "'")
    
    results = cursor.fetchall()

#create an output which will follow key:value where the key is the name of a column and a data are relative data from all rows.
    result = []
    for row in results:
        row_dict = {}
        for i in range(len(column_name)):
            row_dict[column_name[i]] = row[i]
        result.append(row_dict)
    
    return result

class Node(BaseModel):
    uuid: str
    name: str = None
    key: str
    ip: str
    url: str
    master_key: str
    description: str

@LeanIPGrid.post("/v1/node/")
async def add_node(node: Node):
#    print(node.uuid)
#    print(node.name)

#Probably this one must be moved into a dedicated function
    cursor = con.cursor()
    cursor.execute("SELECT key FROM nodes WHERE name = 'MASTER'")
    result = cursor.fetchone()

#    print(result[0])
#    print(node.master_key)
#Validation if the master_key is right one.

    if (result[0] != node.master_key):
        print("MASTER KEY NOT MATCH")
        return 


# let's validate if there is no host with the same IP, name or url    uuid,name,ip,key,url,description,node
    cursor = con.cursor()
    cursor.execute("SELECT * FROM nodes where uuid = '" + node.uuid + "'")
    result = cursor.fetchone()
#    print(result)

    if result:
        print("przerwanie podany uuid istnieje")
        return

    cursor = con.cursor()
    cursor.execute("SELECT * FROM nodes where ip = '" + node.ip + "'")
    result = cursor.fetchone()
    print(result)

    if result:
        print("przerwanie podany ip istnieje")
        return

    cursor = con.cursor()
    cursor.execute("SELECT * FROM nodes where url = '" + node.url + "'")
    result = cursor.fetchone()
    print(result)

    if result:
        print("przerwanie podany url istnieje")
        return

    
# Add new node based on delivered data
    cursor = con.cursor()
    cursor.execute("INSERT INTO nodes (uuid,name,ip,key,url,description,node) VALUES ('" + node.uuid + "','" + node.name + "','" + node.ip + "','" + node.key + "','" + node.url + "','" + node.description + "','')")
    con.commit()
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

@LeanIPGrid.post("/v1/ipv4/network")
async def add_ipv4_network(cidr: str, netmask: str, node_uuid: str):
#Function to add the new network definition with all the required global and local attributes.
# Basics: 
# IP address (range) - can be decimal/binary (must be converted to binary)
# netmask - can be decimal/binary/bits (must be converted to binary)
# 
    if len(cidr) == 32:
        cidr = cidr
    elif 7 <= len(cidr) <= 15:
        cidr =  dec2bin(cidr)
    else:
        return {"ERROR WRONG cidr"}

    if len(netmask) == 32:
        netmask = netmask 
    elif 7 <= len(netmask) <= 15:
        netmask =  dec2bin(netmask)
    elif 1 <= len(netmask) <= 2:
        netmask = ipv4_bit2bin(netmask)
    elif netmask == None:
        netmask = ipv4_bit2bin(32)
    else:
        return {"ERROR WRONG CIDR"}
    

    network_address = ''.join(str(int(bit_ip) & int(bit_mask)) for bit_ip, bit_mask in zip(cidr, netmask))

    logging.info(cidr)
    logging.info(netmask)


    result = "CIDR:" + cidr + " Netmask: " + netmask + " NodeUUID: " + node_uuid + " Network address: " + network_address

    cursor = con.cursor()
    query = "SELECT uuid FROM ipv4_networks WHERE network_address_binary = '" + network_address + "' AND subnet_mask_binary = '" + netmask + "'"

    logging.info(query)
    cursor.execute(query)

    result = cursor.fetchone()

    print(result)

    if result == None:
        print("update bazy")
        network_address_dec = bin2dec(network_address)
        netmask_dec = bin2dec(netmask)
        new_uuid = uuid.uuid4()
        network_broadcast_binary = ipv4_bcast_address(network_address,netmask)
        print('Network bcast binary:')
        logging.info(network_broadcast_binary)
        network_broadcast_dec = bin2dec(network_broadcast_binary)
        logging.info(network_broadcast_dec)
        print('-----')
        query = f"INSERT INTO ipv4_networks \
                    (uuid,network_address,network_address_binary,subnet_mask,subnet_mask_binary, \
                    network_broadcast,network_broadcast_binary,node_uuid) \
                    VALUES \
                    ('{new_uuid}','{network_address_dec}','{network_address}','{netmask_dec}','{netmask}', \
                    '{network_broadcast_dec}','{network_broadcast_binary}','{node_uuid}')"
        logging.info(query)
        con.cursor()
        cursor.execute(query)
        con.commit()
        

    else:
        print("ERROR: requested network already exists in database")

    return result
