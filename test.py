# from time import sleep
#
# from src.core.fsuipc_client import FSUIPCClient
#
# fsuipc_client = FSUIPCClient("lib/libfsuipc.dll")
#
# while True:
#     res = fsuipc_client.open_fsuipc_client()
#     if res.requestStatus:
#         print(f"FSUIPC connection established")
#         break
#     print(f"Failed to open FSUIPC connection")
#     sleep(5)
#
# res = fsuipc_client.get_connection_state()
# print(f"FSUIPC connection state: {res.status}")
#
# while True:
#     res = fsuipc_client.get_frequency()
#     print(res.frequency)
#     com1 = (res.frequencyFlag & 0x80) != 0x80
#     com2 = (res.frequencyFlag & 0x40) != 0x40
#     print(f"COM1: {com1}, COM2: {com2}")
#     sleep(1)
from src.utils import get_device_info

print(get_device_info(0))
