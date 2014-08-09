from migen.fhdl.std import *
from migen.genlib.record import *

def phase_cmd_description(a, ba):
	return [
		("address",			a,		DIR_M_TO_S),	
		("bank",			ba,		DIR_M_TO_S),
		("cas_n",			1,		DIR_M_TO_S),
		("cs_n",			1,		DIR_M_TO_S),
		("ras_n",			1,		DIR_M_TO_S),
		("we_n",			1,		DIR_M_TO_S),
		("cke",				1,		DIR_M_TO_S),
		("odt",				1,		DIR_M_TO_S),
		("reset_n",			1,		DIR_M_TO_S)
	]

def phase_wrdata_description(d):
	return [
		("wrdata",			d,		DIR_M_TO_S),
		("wrdata_en",		1,		DIR_M_TO_S),
		("wrdata_mask",		d//8,	DIR_M_TO_S)
	]

def phase_rddata_description(d):
	return [
		("rddata_en",		1,		DIR_M_TO_S),
		("rddata",			d,		DIR_S_TO_M),
		("rddata_valid",	1,		DIR_S_TO_M)
	]

def phase_description(a, ba, d):
	r = phase_cmd_description(a, ba)
	r += phase_wrdata_description(d)
	r += phase_rddata_description(d)
	return r

class Interface(Record):
	def __init__(self, a, ba, d, nphases=1):
		layout = [("p"+str(i), phase_description(a, ba, d)) for i in range(nphases)]
		Record.__init__(self, layout)
		self.phases = [getattr(self, "p"+str(i)) for i in range(nphases)]
		for p in self.phases:
			p.cas_n.reset = 1
			p.cs_n.reset = 1
			p.ras_n.reset = 1
			p.we_n.reset = 1
	
	# Returns pairs (DFI-mandated signal name, Migen signal object)
	def get_standard_names(self, m2s=True, s2m=True):
		r = []
		add_suffix = len(self.phases) > 1
		for n, phase in enumerate(self.phases):
			for field, size, direction in phase.layout:
				if (m2s and direction == DIR_M_TO_S) or (s2m and direction == DIR_S_TO_M):
					if add_suffix:
						if direction == DIR_M_TO_S:
							suffix = "_p" + str(n)
						else:
							suffix = "_w" + str(n)
					else:
						suffix = ""
					r.append(("dfi_" + field + suffix, getattr(phase, field)))
		return r

class Interconnect(Module):
	def __init__(self, master, slave):
		self.comb += master.connect(slave)
