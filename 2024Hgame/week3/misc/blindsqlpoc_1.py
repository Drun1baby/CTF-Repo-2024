import sys
import pyshark
from urllib.parse import unquote
import re
from loguru import logger
TSHARK_BIN = r"D:\Bag_Install\bag\Wireshark\\tshark.exe"


# set logger level to INFO, ignore debug log
logger.remove()
logger.add(sys.stdout, level="INFO")

requests_base = pyshark.FileCapture("./blindsql.pcapng", display_filter="http.request", tshark_path=TSHARK_BIN)
responses_base = pyshark.FileCapture("./blindsql.pcapng", display_filter="http.response", tshark_path=TSHARK_BIN)
responses = {}

for packet in responses_base:
    responses.update({
        packet.http.request_in: bytes.fromhex(packet.http.file_data.raw_value).decode()
    })

brute = 1
data = ""
low = 1
high = 128

for packet in requests_base:
    query = unquote(packet.http.request_uri_query_parameter)
    response = responses[packet.frame_info.number]
    matches = re.search(r"id=1-\(ascii\(substr\(\((.*?)\),(\d+),1\)\)>(\d+)\)", query)
    expr, index, mid = matches.groups()
    logger.debug(f"frame {packet.frame_info.number}, {expr}")

    if int(index) > brute:
        # char in index `brute` finished, revert low and high mark
        data += chr(high)
        logger.success(f"data {data}")
        brute = int(index)
        low = 1
        high = 128
        
    if int(index) == 1 and int(index) < brute:
        # group finished, revert low and high mark, revert index `brute`
        logger.success(f"data {data}")
        brute = 1
        data = ""
        low = 1
        high = 128

    if "NO!" in response:
        high = int(mid)
    else:
        low = int(mid)

    logger.debug(f"mid {mid}, low {low}, high {high}")