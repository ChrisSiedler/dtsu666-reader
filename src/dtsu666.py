#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ModBusDev as MBD
from pymodbus.constants import Endian


class dtsu666(MBD.ModBusDev):

	def __init__(self, *args, **kwargs):
		self.model = "dtsu666"
		self.baud = 9600

		self.wordorder = Endian.Big
		self.byteorder = Endian.Big

		super().__init__(*args, **kwargs)

		self.registers = {
#									address, length, rtype, 			dtype, 							vtype, 	label, fmt, sf

#			"Volts_AB":  			(0x2000, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Volts_AB", "V", 0.1),
#			"Volts_BC":  			(0x2002, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Volts_BC", "V", 0.1),
#			"Volts_CA":  			(0x2004, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Volts_CA", "V", 0.1),

			"U_A":  				(0x2006, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Volts N-L1", "V", 0.1),
			"U_B":  				(0x2008, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Volts N-L2", "V", 0.1),
			"U_C":  				(0x200A, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Volts N-L3", "V", 0.1),

			"I_A":  				(0x200C, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Current L1", "A", .001),
			"I_B":  				(0x200E, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Current L2", "A", .001),
			"I_C":  				(0x2010, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Current L2", "A", .001),
			
			"P_tot": 		 		(0x2012, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Power Total netto", "W", .1),
			"Qt":  					(0x201A, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Conjunction reactive power", "var", .1),
			
			"P_A":  				(0x2014, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Active Power L1", "W", .1),
			"P_B":  				(0x2016, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Active Power L2", "W", .1),
			"P_C":  				(0x2018, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Active Power L3", "W", .1),

			"Q_A":  				(0x201c, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "reactive Power L1", "var", .1),
			"Q_B":  				(0x201e, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "reactive Power L2", "var", .1),
			"Q_C":  				(0x2020, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "reactive Power L3", "var", .1),
			
			"L3_PF":  				(0x2030, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "power factor L3", "", .001),
			"DmPt":  				(0x2050, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Total active powerdemand", "W", .1),

			"F":  					(0x2044, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Frequency", "Hz", .01),
			
			"Etot_imp":  			(0x401e, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Energy Total import", "kWh", 1),
			"Etot_exp":  			(0x4028, 2, MBD.registerType.HOLDING, MBD.registerDataType.FLOAT32, float, "Energy Total export", "kWh", 1),
			
			
			"IrAt":  				(0x0006, 1, MBD.registerType.HOLDING, MBD.registerDataType.INT16, float, "Current Transformer Ratio", "", 1),
			"UrAt":  				(0x0007, 1, MBD.registerType.HOLDING, MBD.registerDataType.INT16, float, "Potential Transformer Ratio", "", 0.1),

			"Addr":  				(0x002d, 1, MBD.registerType.HOLDING, MBD.registerDataType.INT16, int, "Communication address", "", 1),
			"Sec":  				(0x002f, 1, MBD.registerType.HOLDING, MBD.registerDataType.INT16, int, "Sec", "", 1),
			"Min":  				(0x0030, 1, MBD.registerType.HOLDING, MBD.registerDataType.INT16, int, "Min", "", 1),
			"Month":  				(0x0033, 1, MBD.registerType.HOLDING, MBD.registerDataType.INT16, int, "Month", "", 1),
			"Year":  				(0x0034, 1, MBD.registerType.HOLDING, MBD.registerDataType.INT16, int, "Year", "", 1),


		}

