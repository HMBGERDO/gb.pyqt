from subprocess import Popen, PIPE
from ipaddress import ip_address
from tabulate import tabulate


RESULT_SUCCESS = "sucessed"
RESULT_FAILED = "failed"


def host_ping(ip_address_list:list, timeout:int=500, requests:int=1) -> None:
    result = []
    tasks = []
    for ip in ip_address_list:
        try:
            ip = ip_address(ip)
        except ValueError:
            pass
        tasks.append((ip, Popen(f'ping {ip} -w {timeout} -n {requests}', shell=False, stdout=PIPE)))
    for ip, task in tasks:            
        respond = task.wait()
        if respond == 0:
            result.append((ip, RESULT_SUCCESS))
        else:
            result.append((ip, RESULT_FAILED))
    return result

def host_range_ping(start_ip_address:str, range_amount:int) -> None:
    start_ip_address = ip_address(start_ip_address)
    address_list = []
    for i in range(range_amount):
        address_list.append(start_ip_address + i)
    return(host_ping(address_list))

def host_range_ping_tab(start_ip_address:str, range_amount:int) -> None:
    result = host_range_ping(start_ip_address, range_amount)
    result_tab = {"successed":[], "failed":[]}
    for ip, status in result:
        if status == RESULT_SUCCESS:
            result_tab["successed"].append(ip)
        elif status == RESULT_FAILED:
            result_tab["failed"].append(ip)
    print(tabulate(result_tab, headers=["successed", "failed"]))

if __name__ == '__main__':
    ip_addresses = ['yandex.ru', '2.2.2.2', '192.168.0.100', '192.168.0.101']
    print(host_ping(ip_addresses))

    print(host_range_ping("192.168.1.100", 5))

    host_range_ping_tab("192.168.1.100", 5)