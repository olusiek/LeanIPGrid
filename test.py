import sqlite3

con = sqlite3.connect("leanipgrid.db")

debug = 1

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

        ipv4_network_finder(cidr,netmask)
    else: 
        print("----------------------------------")
        print(result)
        print("----------------------------------")

#        print("ZNALAZLEM DOPASOWANIE: " + result["network_address"])

#        netmask_dec = bin2dec(netmask)
#        print("decimal value: " + netmask_dec)

    

    return result

def bin2dec(binary_mask):
#this function makes a transformation of binary IPv4 notation into decimal one (for both ip and subnet mask)
    result = ''
    octets = [binary_mask[i:i+8] for i in range(0, len(binary_mask), 8)]
    decimal_octets = [int(octet, 2) for octet in octets]
    result = '.'.join(map(str, decimal_octets))

    return result


netmask = str("11111111111111110000000000000000")
cidr = str("00001010000000000000000000000000")

print(ipv4_network_finder(cidr,netmask))