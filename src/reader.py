#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dtsu666 import dtsu666
import ModBusDev as MBD

#RS485Port = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.1.2:1.0-port0' # Smartmeter
RS485Port = '/dev/ttyUSB0' # loopback test

if __name__ == "__main__":

    meter = dtsu666(
        device=RS485Port,
        stopbits=1,
        parity="N",
        baud=9600,
        timeout=1,
        unit=4
    )

    print(f"{meter}:")
#    print("\nInput Registers:")

#    for k, v in meter.read_all(MBD.registerType.INPUT).items():
#        address, length, rtype, dtype, vtype, label, fmt, sf = meter.registers[k]
#
#        if type(fmt) is list or type(fmt) is dict:
#            print(f"\t{label}: {fmt[str(v)]}")
#        elif vtype is float:
#            print(f"\t{label}: {v:.2f}{fmt}")
#        else:
#            print(f"\t{label}: {v}{fmt}")

    print("\nHolding Registers:")

    for k, v in meter.read_all(MBD.registerType.HOLDING).items():
        address, length, rtype, dtype, vtype, label, fmt, sf = meter.registers[k]

        if type(fmt) is list:
            print(f"\t{label}: {fmt[v]}")
        elif type(fmt) is dict:
            print(f"\t{label}: {fmt[str(v)]}")
        elif vtype is float:
            print(f"\t{label}: {v:.2f}{fmt}")
        else:
            print(f"\t{label}: {v}{fmt}")
