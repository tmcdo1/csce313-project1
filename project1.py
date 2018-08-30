"""
Thomas McDonald
925005933
CSCE 315-504
Due: September 10, 2018 (or whatever the due date is)
project1.py
"""
from contextlib import closing
from socket import socket, AF_INET, SOCK_DGRAM
import sys
import struct
import time

import math
from tkinter import *

servers = ["0.us.pool.ntp.org",
"2.us.pool.ntp.org",
"1.us.pool.ntp.org",
"0.ubuntu.pool.ntp.org",
"1.ubuntu.pool.ntp.org",
"2.ubuntu.pool.ntp.org",
"3.ubuntu.pool.ntp.org",
"ntp.ubuntu.com",
"time.apple.com",
"time.windows.com",
"time1.google.com",
"time2.google.com",
"time3.google.com",
"time4.google.com",
"ntp1.tamu.edu",
"ntp2.tamu.edu",
"ntp3.tamu.edu",
"ops1.engr.tamu.edu",
"ops2.engr.tamu.edu",
"ops3.engr.tamu.edu",
"ops4.engr.tamu.edu",
"filer.cse.tamu.edu",
"compute.cse.tamu.edu",
"linux2.cse.tamu.edu",
"dns1.cse.tamu.edu",
"dns2.cse.tamu.edu",
"dhcp1.cse.tamu.edu",
"dhcp2.cse.tamu.edu"]

NTP_PACKET_FORMAT = "!12I"
NTP_DELTA = 2208988800 # 1970-01-01 00:00:00
NTP_QUERY = '\x1b' + 47 * '\0'

"""
python3 code to query an NTP time server
Based on https://stackoverflow.com/questions/12664295/ntp-client-in-python
"""
def ntp_time(host="pool.ntp.org", port=123):
    try:
        with closing(socket( AF_INET, SOCK_DGRAM)) as s:
            # Set timeout for socket connection to 5 seconds
            s.settimeout(5)
            s.sendto(NTP_QUERY.encode('utf-8'), (host, port))
            msg, address = s.recvfrom(1024)
        unpacked = struct.unpack(NTP_PACKET_FORMAT,msg[0:struct.calcsize(NTP_PACKET_FORMAT)])
        return unpacked[10] + float(unpacked[11]) / 2**32 - NTP_DELTA
    except:
        print(host, 'timed out...')
        return -1

svr_time_diffs = {}
discrepancies = {}

# Computes the average time difference of all the servers exept the given name
def get_average(svr_name):
    temp_svrs_diffs = svr_time_diffs.copy()
    temp_svrs_diffs.pop(svr_name)
    diff_sum = sum(temp_svrs_diffs.values())
    return diff_sum/len(temp_svrs_diffs.keys())

if __name__ == "__main__":
    # Query NTP servers for the time
    for server in servers:
        print("Requesting: ", server)
        svr_time = ntp_time(host=server)
        if svr_time > 0:
            svr_time_diffs[server] = svr_time - time.time()

    # Compute discrepancies for each server
    for server in svr_time_diffs:
        discrepancies[server] = abs(svr_time_diffs[server] - get_average(server))

    # Get the max discrepancy
    if len(discrepancies.items()) > 0:
        max_svr_name = max(discrepancies, key=discrepancies.get)
        print("\n{} has the max discrepancy of {}".format(max_svr_name, discrepancies[max_svr_name]))

        # Create histograms
        window = Tk()

        num_items = len(discrepancies.items())

        initial_spacing = 30
        text_spacing = 150
        bar_spacing = 5
        bar_height = 25

        canvas_width = 700
        canvas_height = initial_spacing + (num_items)*bar_spacing + bar_height*num_items

        bar_width_scale = (canvas_width-text_spacing)/discrepancies[max_svr_name]*0.9

        graph_base_x = text_spacing

        hist_canvas = Canvas(window, width=canvas_width, height=canvas_height)
        hist_canvas.pack()

        # Create grid lines on side of histogram
        for i in range(graph_base_x, canvas_width-10, 70):
            label = "{}s".format(round(abs((i-graph_base_x)/bar_width_scale)*1000)/1000)
            hist_canvas.create_text(i,0,text=label, anchor=N)
            hist_canvas.create_line(i,15,i,25)

        # Draw bars for each server with a response
        y = initial_spacing
        for k, v in discrepancies.items():
            bar_width = v*bar_width_scale
            if(v > 1):
                hist_canvas.create_rectangle(graph_base_x, y, graph_base_x+bar_width, y+bar_height, fill='red', outline='red')
            else:
                hist_canvas.create_rectangle(graph_base_x, y, graph_base_x+bar_width, y+bar_height, fill='green', outline='green')

            hist_canvas.create_text(5,y+.5*bar_height, text=k, anchor=W)
            y += bar_spacing + bar_height

        window.mainloop()
    else:
        print('No data could be obtained')
