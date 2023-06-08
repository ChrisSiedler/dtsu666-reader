#!/usr/bin/python3
# -*- coding: utf-8 -*-

import enum
import time
import logging

from pymodbus.constants import Endian
#from pymodbus.client.sync import ModbusSerialClient as ModbusSerialClient
from pymodbus.client.serial import ModbusSerialClient
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.register_read_message import ReadInputRegistersResponse
from pymodbus.register_read_message import ReadHoldingRegistersResponse


class connectionType(enum.Enum):
    RTU = 1
    TCP = 2


class registerType(enum.Enum):
    INPUT = 1
    HOLDING = 2


class registerDataType(enum.Enum):
	BITS = 1
	UINT8 = 2
	UINT16 = 3
	UINT32 = 4
	UINT64 = 5
	INT8 = 6
	INT16 = 7
	INT32 = 8
	INT64 = 9
	FLOAT16 = 10
	FLOAT32 = 11
	STRING = 12
	RAW = 13


RETRIES = 3
TIMEOUT = 1
UNIT = 1


class ModBusDev:
	model = "Generic"
	registers = {}

	stopbits = 1
	parity = "N"
	baud = 38400

	wordorder = Endian.Big
	byteorder = Endian.Big
	bytesperregister = 2
	charset = "ascii"
	batchlimit = 75

	def __init__(self, **kwargs):
		parent = kwargs.get("parent")

		if parent:
		    self.client = parent.client
		    self.mode = parent.mode
		    self.timeout = parent.timeout
		    self.retries = parent.retries

		    unit = kwargs.get("unit")

		    if unit:
		        self.unit = unit
		    else:
		        self.unit = parent.unit

		    if self.mode is connectionType.RTU:
		        self.device = parent.device
		        self.stopbits = parent.stopbits
		        self.parity = parent.parity
		        self.baud = parent.baud
		    elif self.mode is connectionType.TCP:
		        self.host = parent.host
		        self.port = parent.port
		    else:
		        raise NotImplementedError(self.mode)
		else:
		    self.timeout = kwargs.get("timeout", TIMEOUT)
		    self.retries = kwargs.get("retries", RETRIES)
		    self.unit = kwargs.get("unit", UNIT)

		    device = kwargs.get("device")

		    if device:
		        self.device = device

		        if ( stopbits := kwargs.get("stopbits") ):
		            self.stopbits = stopbits

		        parity = kwargs.get("parity")

		        if parity and parity.upper() in ["N", "E", "O"]:
		            self.parity = parity.upper()
		        else:
		            self.parity = False

		        baud = kwargs.get("baud")

		        if baud:
		            self.baud = baud

		        self.mode = connectionType.RTU
		        self.client = ModbusSerialClient(
		            method="rtu",
		            port=self.device,
		            stopbits=self.stopbits,
		            parity=self.parity,
		            baudrate=self.baud,
		            timeout=self.timeout
		        )
		    else:
		        self.host = kwargs.get("host")
		        self.port = kwargs.get("port", 502)
		        self.mode = connectionType.TCP

		        self.client = ModbusTcpClient(
		            host=self.host,
		            port=self.port,
		            timeout=self.timeout
		        )

		self.connect()

	def _clean_data(self, results):
		return results

	def __repr__(self):
		if self.mode == connectionType.RTU:
		    return f"{self.model}({self.device}, {self.mode}: stopbits={self.stopbits}, parity={self.parity}, baud={self.baud}, timeout={self.timeout}, retries={self.retries}, unit={hex(self.unit)})"
		elif self.mode == connectionType.TCP:
		    return f"{self.model}({self.host}:{self.port}, {self.mode}: timeout={self.timeout}, retries={self.retries}, unit={hex(self.unit)})"
		else:
		    return f"<{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))}>"

	def _read_input_registers(self, address, length):
		for i in range(self.retries):
		    if not self.connected():
		        self.connect()
		        time.sleep(0.1)
		        continue

		    result = self.client.read_input_registers(address=address, count=length, slave=self.unit)

		    if not isinstance(result, ReadInputRegistersResponse):
		        continue
		    if len(result.registers) != length:
		        continue

		    return BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=self.byteorder, wordorder=self.wordorder)
		return None

	def _read_holding_registers(self, address, length):
		for i in range(self.retries):
		    if not self.connected():
		        self.connect()
		        time.sleep(0.1)
		        continue

		    result = self.client.read_holding_registers(address=address, count=length, slave=self.unit)

		    if not isinstance(result, ReadHoldingRegistersResponse):
		        continue
		    if len(result.registers) != length:
		        logging.warning(f"{address}:{length} requested, but only {len(result.registers)} recieved")
		        continue

		    return BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=self.byteorder, wordorder=self.wordorder)
		return None

	def _write_holding_register(self, address, value):
		return self.client.write_registers(address=address, values=value, slave=self.unit)

	def _encode_value(self, data, dtype):
		builder = BinaryPayloadBuilder(byteorder=self.byteorder, wordorder=self.wordorder)

		try:
		    if dtype == registerDataType.FLOAT32:
		        builder.add_32bit_float(data)
		    elif dtype == registerDataType.INT32:
		        builder.add_32bit_int(data)
		    elif dtype == registerDataType.UINT32:
		        builder.add_32bit_uint(data)
		    elif dtype == registerDataType.INT16:
		        builder.add_16bit_int(int(data))
		    elif dtype == registerDataType.UINT16:
		        builder.add_16bit_uint(int(data))
		    else:
		        raise NotImplementedError(dtype)
		except NotImplementedError:
		    raise

		return builder.to_registers()

	def _decode_value(self, rawdata, bytes, dtype, vtype):
		data = rawdata

		if   dtype in [registerDataType.INT16, registerDataType.UINT16] and bytes != 2:
			raise ValueError(f"incorrect data length {bytes}B for type: {dtype}")

		elif dtype in [registerDataType.FLOAT32, registerDataType.INT32, registerDataType.UINT32] and bytes != 4:
			raise ValueError(f"incorrect data length {bytes}B for type: {dtype}")

		try:
			if dtype == registerDataType.FLOAT32:
				return vtype(data.decode_32bit_float())
			elif dtype == registerDataType.INT32:
				return vtype(data.decode_32bit_int())
			elif dtype == registerDataType.UINT32:
				return vtype(data.decode_32bit_uint())
			elif dtype == registerDataType.INT16:
				return vtype(data.decode_16bit_int())
			elif dtype == registerDataType.UINT16:
				return vtype(data.decode_16bit_uint())
			elif dtype == registerDataType.STRING:
				return vtype(data.decode_string(bytes).decode(self.charset))
			elif dtype == registerDataType.RAW:
#				return [data.decode_bits() for x in range(bytes)]
				return vtype([hex(data.decode_8bit_int()) for x in range(bytes)])
			else:
				raise NotImplementedError(dtype)
		except NotImplementedError:
			raise

	def _read(self, value):
		address, length, rtype, dtype, vtype, label, fmt, sf = value

		try:
			if rtype == registerType.INPUT:
				rawdata = self._read_input_registers(address, length)
			elif rtype == registerType.HOLDING:
				rawdata = self._read_holding_registers(address, length)
			else:
				raise NotImplementedError(rtype)

			return self._decode_value(rawdata, (length * self.bytesperregister), dtype, vtype)

		except NotImplementedError:
			raise

	def _read_all(self, values, rtype):
		results = {}

		if values == []: # if empty request
			return results

		addr_min = values[0][1]
		addr_max = values[-1][1] + values[-1][2]
		offset = addr_min
		length = addr_max - addr_min
#		print(f"addr min: {addr_min}, max: {addr_max}")

		try:
			if rtype == registerType.INPUT:
				data = self._read_input_registers(offset, length)
			elif rtype == registerType.HOLDING:
				data = self._read_holding_registers(offset, length)
			else:
				raise NotImplementedError(rtype)

			if not data:
				return results

			for v in values:
				k, address, length, rtype, dtype, vtype, label, fmt, sf = v

				if address > offset:
					skip_bytes = address - offset
					offset += skip_bytes
					data.skip_bytes(skip_bytes * 2)
				elif address < offset:
					raise ValueError(f"{k}: can't move from addr {offset} back to {address}")
					
				try:
					val = self._decode_value(data, (length * self.bytesperregister), dtype, vtype)
				except Exception as e:
					logging.error(f"Error decoding: {v}, data, error:{e}")
					continue

				if isinstance(fmt, list) and isinstance(val, int):
					val = fmt[val]
				elif sf != 1:
					val *= sf

				results[k] = val
				offset += length
		except NotImplementedError:
		    raise

		return results

	def _write(self, value, data):
		address, length, rtype, dtype, vtype, label, fmt, sf = value

		try:
		    if rtype == registerType.HOLDING:
		        return self._write_holding_register(address, self._encode_value(data, dtype))
		    else:
		        raise NotImplementedError(rtype)
		except NotImplementedError:
		    raise

	def connect(self):
		return self.client.connect()

	def disconnect(self):
		self.client.close()

	def connected(self):
		return self.client.is_socket_open()

	def get_scaling(self, key):
		address, length, rtype, dtype, vtype, label, fmt, sf = self.registers[key]
		return sf

	def read(self, key, scaling=True):
		if key not in self.registers:
		    raise KeyError(key)

		if scaling:
		    return self._read(self.registers[key]) * self.get_scaling(key)
		else:
		    return self._read(self.registers[key])

	def write(self, key, data):
		if key not in self.registers:
		    raise KeyError(key)

		return self._write(self.registers[key], data / self.get_scaling(key))

	def read_all(self, rtype=registerType.INPUT):
		registers = [(k, *v) for k, v in self.registers.items() if (v[2] == rtype)]
		registers.sort(key=lambda a: a[1]) # sort by register addr
		results = {}

		startadr = 0
		batches = []
		batchi = []
		for v in registers:
			addrend = v[1] + v[2]
			if addrend > (self.batchlimit + startadr):
				startadr = v[1]
				batches.append(batchi)
				batchi = []
			
			batchi.append(v)
		else:
			batches.append(batchi)
	
		for batch in batches:
		    results.update(self._read_all(batch, rtype))

		results = self._clean_data(results)
		return results

	# ----------------------------------------------------------------------------------	
	def read_list(self, items):
	
		reglist = [(k, *v) for k, v in self.registers.items() if (k in items)]
			
		results = {}
		for rtype in registerType:
			registers = [v for v in reglist if (v[3] == rtype)]
			registers.sort(key=lambda a: a[1]) # sort by register addr

			startadr = 0
			batches = []
			batchi = []
			for v in registers:
				addrend = v[1] + v[2]
				if addrend > (self.batchlimit + startadr):
					startadr = v[1]
					batches.append(batchi)
					batchi = []
				
				batchi.append(v)
			else:
				batches.append(batchi)
		
			for batch in batches:
			    results.update(self._read_all(batch, rtype))

		results = self._clean_data(results)
		return results
		
