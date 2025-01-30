import time
import threading
import can
from drivers.CElectric import CElectric
from drivers.LoadCell import LoadCell
from drivers.AMT212 import AMT212
from drivers.EndStop import EndStop
from drivers.Roboteq import Roboteq
from drivers.SidekickInternal import Sidekick
from CAN_Parsing import *
import traceback
from statistics import mean
import csv

from rich import box
from rich.console import Console
from rich.live import Live
from rich.table import Table,Column
from rich import print,logging
from rich.layout import Layout

l = threading.Lock()

canNodes = []
canTableData = {}
startTime = time.time()
intervalData = {}
errCounter = 0
#Order: "Source", "CAN-ID", "DLC", "Data", "Interpretation", "Time\n(s)", "timestamp\n(s)", "interval\n(ms)", "Max int\n(ms)"


def dictToStr(d):
    #return str(d)
    return "\n".join(["{}:{}".format(k,v) for (k,v) in d.items()])#str(d)

def dataToHex(data):
    return " ".join(["{:02X}".format(b) for b in data])

def updateInterval(id,t):
    if id not in intervalData:
        intervalData[id] = {"prevT":t, "intervals":[]}
        return []
    else:
        prevT = intervalData[id]["prevT"]
        curInterval = t - prevT
        intervalData[id]["intervals"].append(curInterval)
        if(len(intervalData[id]["intervals"])>=100):
            intervalData[id]["intervals"].pop(0)
        intervalData[id]["prevT"] = t
        return intervalData[id]["intervals"]

def processMsg(msg:can.Message):
    global canTableData
    #print(f"rx: {msg}")
    now = time.time()
    id = msg.arbitration_id
    source = "Unknown"
    dlc = str(msg.dlc)
    dataHex = dataToHex(msg.data)
    interpretation = ""
    style = "on orange_red1"
    intervals = updateInterval(hex(id),now)
    meanInterval = "{:.1f}".format(1000*mean(intervals)) if len(intervals)>0 else "-"
    maxInterval = "{:.1f}".format(1000*max(intervals)) if len(intervals)>0 else "-"
    #matched = False
    for (src, st, node) in canNodes:
        if(id in node.CAN_Rx_IDs()):
            #matched = True
            parsedData = node.parseMsg(msg)
            if parsedData is not None:
                source = src
                style = st
                interpretation = dictToStr(parsedData)
                break
    rowData = [source,
            hex(id),
            dlc,
            dataHex,
            interpretation,
            "{:.4f}".format(now-startTime),
            "{:.4f}".format(msg.timestamp),
            meanInterval,
            maxInterval]
    with open('CANlog.csv','a') as f:
        writer = csv.writer(f)
        writer.writerow(rowData)
    l.acquire()
    canTableData[hex(id)] = (style, rowData)
    l.release()

def create_live_table(height,tableTitle) -> Table:
    global canTableData
    table = Table(
        "Source","CAN-ID", "DLC", "Data", Column(header="Interpretation", width=20), "Time\n(s)", "timestamp\n(s)", "Mean recent\ninterval (ms)", "Max recent\ninterval (ms)",
        box=box.HORIZONTALS,
        show_lines=True,
        expand=True)
    l.acquire()
    for id in canTableData.keys():
        (st,data)=canTableData[id]
        table.add_row(*data,style=st)
    l.release()
    return table

def receive(bus, stop_event):
    """The loop for receiving."""
    global canTableData
    global canNodes
    global errCounter
    print("Start receiving messages")
    startTime = time.time()
    while not stop_event.is_set():
        try:
            rx_msg = None
            try:
                rx_msg = bus.recv(1)
            except:
                l.acquire()
                errCounter+=1
                l.release()
                #print(f"CAN framing error | Time: {time.time()-startTime} | ErrorCount: {errCounter}")
                #traceback.print_exc()
            if rx_msg is not None:
                processMsg(rx_msg)

        except Exception:
            traceback.print_exc()
            stop_event.set()
            bus.shutdown()
    print("Stopped receiving messages")

def makeLayout() -> Layout:
    layout = Layout("root")
    layout.split(
        Layout(name="CAN Monitor", ratio=1),
        Layout(name="Info", size=1 )
    )
    return layout

def updateLayout(layout,footerData) -> Layout:
    layout["CAN Monitor"].update(create_live_table(" "," "))
    layout["Info"].update(footerData)
    return layout

def main():
    global canNodes
    #with can.ThreadSafeBus(chanel="can0", bustype="socketcan", bitrate=500000) as bus:
    try:
        with can.ThreadSafeBus(channel="/dev/can_roboteq", bustype="serial", baudrate=500000) as bus:
            with open("CANlog.csv", 'w') as csvfile:
                csvwriter = csv.writer(csvfile)
                headerRow =["Source","CAN-ID", "DLC", "Data", "Interpretation", "Time\n(s)", "timestamp\n(s)", "Mean recent\ninterval (ms)", "Max recent\ninterval (ms)"]
                csvwriter.writerow(headerRow)

            # Source label, table entry color, node
            ce =            ("CElectric"    ,"on green"             ,CElectric(bus=bus))
            lc =            ("LoadCell"     ,"on blue"              ,LoadCell(bus=bus))
            absEncoder =    ("AbsEncoder"   ,"on cyan"              ,AMT212(bus=bus))
            es =            ("EndStop"      ,"on dark_violet"       ,EndStop(bus=bus))
            rbtq =          ("Roboteq"      ,"on deep_sky_blue4"    ,Roboteq(bus=bus, nodeID = 1))
            side =          ("Sidekick"     ,"on grey54"            ,Sidekick(bus=bus))
            canNodes =  [ce,lc,absEncoder,es,rbtq,side]

            stop_event = threading.Event()
            t_receive = threading.Thread(target=receive, args=(bus, stop_event))
            t_receive.start()
            side[2].requestVersionNumber()

            console = Console()

            layout = makeLayout()
            try:
                with Live(layout, screen=True, auto_refresh=False) as live:
                    while True:
                        #live.update(create_live_table(console.size.height - 4, "{} | {}".format(side[2].HWversion,side[2].FWversion)), refresh=True)
                        live.update(updateLayout(layout, "{} | {} | [red]Errors: {}[/red]".format(side[2].HWversion,side[2].FWversion, errCounter)), refresh=True)
                        time.sleep(0.01)

            except KeyboardInterrupt:
                pass  # exit normally

            stop_event.set()
            time.sleep(0.5)
    except Exception as e:
        print(e)
        #traceback.print_exc()


if __name__ == "__main__":
    main()
