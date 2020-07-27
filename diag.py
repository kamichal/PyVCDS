#!/usr/bin/env python3

import sys
import io
import argparse
import can
import obd2
import threading

def recv(socket, stack):
  while True:
    stack._recv(socket.recv)

def selector(lst):
  while True:
    try:
      print("Do What?")
      for i in range(len(lst)):
        print("{}: {}".format(i,lst[i]))
      iput = input("> ")
      ret = int(iput)
      if ret < len(lst):
        return ret
    except FormatError:
      print("Enter the integer value of the selected option")

def dselector(dct, header="Do What?"):
  while True:
    try:
      print(header)
      for k,v in dct.items():
        print("{}: {}".format(k,v))
      ret = input("> ")
      if ret in dct:
        return ret
    except FormatError:
      print("Enter the integer value of the selected option")

def advanced():
  pass

def oem(vin):
  global socket
  while True:
    if vin.startswith("WVW"):
      import vwtp, kwp, vw
      stack = vwtp.VWTPStack(socket)
      with vw.VWVehicle(stack) as car:
        opt = ["Enumerate Modules", "Read DTCs by module", "Read Measuring Data Block by module", "Long-Coding", "Back"]
        op = selector(opt)
        if op == 0:
          print("Enumerating modules, please wait")
          car.enum()
          print("Modules Available:")
          for mod in car.enabled:
            print(" ",vw.modules[mod])
        elif op == 1:
          for mod in car.enabled:
            print("Checking module '{}'".format(vw.modules[mod]))
            with car.module(mod) as m:
              dtc = m.getDTC()
              if len(dtc) > 0:
                print("Found DTCs:")
              else:
                print("No Faults detected")
              for d in dtc:
                if d in vw.labels[module]["dtc"]:
                  print(vw.labels[module]["dtc"][d])
                else:
                  print("Unknown DTC '{}'".format(d))
        elif op == 2: #read measuring block
          mods = {}
          for i in car.enabled:
            mods[i] = vw.modules[i]
          op2 = dselector(mods)
          with car.module(mod) as mod:
            blk = dselector(vw.labels[module]["blocks"])
            mod.readBlock(blk)
        elif op == 3: #long-code
          raise NotImplementedError("Need a CAN trace of someone with VCDS reading or writing a long-code")
        elif op == 4:
          return
        

def menu():
  global obd
  global vin
  opt = [ "Display VIN", "OEM Extended Diagnostics", "Inspection Readyness", "Display DTCs", "Advanced/Debugging", "Exit" ]
  print("PyVCDS")
  op = selector(opt)
  if op == 0:
    print(vin)
  elif op == 1:
    oem(vin)
  elif op == 2:
    raise NotImplementedError("Inspection Readyness PID not implemented")
  elif op == 3:
    raise NotImplementedError("Display DTCs not implemented")
  elif op == 4:
    advanced()
  elif op == 5:
    print ("Goodbye")
    sys.exit(0)

p = argparse.ArgumentParser(description="OBD-2 diagnostic utility for SocketCAN")
p.add_argument("--bus", dest='bus', type=str, default=None, help="The CAN bus interface to use")
p.add_argument("--vin", dest='vin', action='store_const', const=True, default=False, help="Print the VIN and exit")
p.add_argument("--bitrate", dest='bits', type=int, default=None, help="The CAN bus bitrate to use")

args = p.parse_args()

if args.bus:
  bus = args.bus
else:
  print("Enter the CAN bus interface to be used (can0):")
  bus = input(">")
  if bus == "":
    bus = "can0"

if args.bits:
  raise NotImplementedError("Dynamic bitrate selection is not yet supported")

sock = can.interface.Bus(channel=bus, bustype='socketcan')
obd = obd2.OBD2Interface(sock)

recvthread = threading.Thread(target=recv,args=(sock,obd))
recvthread.start()

vin = obd.getVIN()

recvthread.stop()

if args.vin:
  print(vin)  
  sys.exit(0)

while True:
  menu()