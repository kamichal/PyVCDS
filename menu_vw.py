import menu
import struct
import vw
import kwp

def mod_menu(car):
  mod = menu.dselector({k:v for k,v in vw.modules.items() if k in car.enabled })
  mod = car.module(mod)
  with mod as m:
    while True:
      op = menu.selector(["Read Module ID", "Read Manufacturer Info", "Read Firmware Version", "Read Coding", "Re-Code module (EXPERIMENTAL)", "Read Measuring Block", "Back"])
      if op == 0:
        print(m.readID())
      if op == 1:
        print(m.readManufactureInfo())
      if op == 2:
        print(m.readFWVersion())
      if op == 3:
        print("Not Yet Implemented")
      if op == 4:
        raise NotImplementedError("Writing module coding is currently unavailable")
      if op == 5:
        
      if op == 6:
        break

def menu(sock):
    with vwtp.VWTPStack(sock) as stack, vw.VWVehicle(stack) as car: #host the connection outside the menu loop.
      while True:
        opt = ["Enumerate Modules", "Connect to Module", "Read DTCs by module", "Read Measuring Data Block by module", "Long-Coding", "Load Labels from VCDS", "Load Labels from JSON", "Back"]
        op = menu.selector(opt)
        if op == 0:
          print("Enumerating modules, please wait")
          car.enum()
          print("Modules Available:")
          for mod in car.enabled:
            print(" ",vw.modules[mod])
        elif op == 1: #Connect to Module
          if not car.scanned:
            car.enum()
          mod_menu(car)
        elif op == 2:
          if not car.scanned:
            car.enum() #TODO: persistent `car` instance
          for mod in car.enabled:
            print("Checking module '{}'".format(vw.modules[mod]))
            try:
              with car.module(mod) as m:
                dtc = m.readDTC()
                if len(dtc) > 0:
                  print("Found DTCs:")
                else:
                  print("No Faults detected")
                for d in dtc:
                  if d in vw.labels[module]["dtc"]:
                    print(vw.labels[module]["dtc"][d])
                  else:
                    print("Unknown DTC '{}'".format(d))
            except kwp.EPERM:
              print("Permissions error getting DTCs from module, skipping")
            except (ValueError, queue.Empty, kwp.KWPException):
              print("Unknown fault getting DTCs from module, skipping")
        elif op == 3: #read measuring block
          mods = {}
          for i in car.enabled:
            mods[i] = vw.modules[i]
          op2 = dselector(mods)
          with car.module(mod) as mod:
            blk = menu.dselector(vw.labels[module]["blocks"])
            blk = mod.readBlock(blk)
            for b in blk:
              print(b)
        elif op == 4: #long-code
          raise NotImplementedError("Need a CAN trace of someone with VCDS reading or writing a long-code")
        elif op == 5:
          raise NotImplementedError("VCDS Label parsing has not yet been implemented")
        elif op == 6:
          print("Path to the JSON file?")
          path = input("> ")
          fd = open(path, "r")
          js = fd.read()
          fd.close()
          vw.loadLabelsFromJSON(js)
        elif op == 7:
          return