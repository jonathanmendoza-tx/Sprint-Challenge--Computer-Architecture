"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
PUSH = 0b01000101
POP = 0b01000110
CMP = 0b10100111
ADD = 0b10100000
MUL = 0b10100010
AND = 0b10101000
DIV = 0b10100011
JEQ = 0b01010101
JNE = 0b01010110
JMP = 0b01010100

class CPU:
	"""Main CPU class."""

	def __init__(self):
		"""Construct a new CPU."""

		self.memory = [0] * 8

		self.ram = [0] * 256

		self.registers = [0] * 8

		self.registers[7] = 0xF4

		self.flags = [0] * 8

		self.pc = 0

		self.branch_table = {
			HLT: self.hlt,
			LDI: self.ldi,
			PRN: self.prn,
			PUSH: self.push,
			POP: self.pop,
			CMP: self.alu,
			ADD: self.alu,
			MUL: self.alu,
			AND: self.alu,
			DIV: self.alu,
			JEQ: self.jeq,
			JNE: self.jne,
			JMP: self.jmp

		}


	def load(self):
		"""Load a program into memory."""

		if (len(sys.argv)) != 2:
			print("remember to pass the second file name")
			print("usage: python3 fileio.py <second_file_name.py>")
			sys.exit()

		address = 0
		try:
			with open(sys.argv[1]) as f:
				for line in f:
					# parse the file to isolate the binary opcodes
					possible_number = line[:line.find('#')]
					if possible_number == '':
						continue # skip to next iteration of loop
					
					instruction = int(possible_number, 2)

					self.ram[address] = instruction

					address += 1

		except FileNotFoundError:
			print(f'Error from {sys.argv[0]}: {sys.argv[1]} not found')
			sys.exit()

	def ram_read(self, MAR):
		#Memory address register
		return self.ram[MAR]

	def ram_write(self, MAR, MDR):
		#MDR: Memory data register
		self.ram[MAR] = MDR

	def alu(self, IR, operand_a, operand_b):
		"""ALU operations."""

		if IR == MUL:
			self.registers[operand_a] *= self.registers[operand_b]

		elif IR == CMP:
			if self.registers[operand_a] < self.registers[operand_b]:
				self.flags = [0] * 8
				self.flags[5] = 1

			elif self.registers[operand_a] > self.registers[operand_b]:
				self.flags = [0] * 8
				self.flags[6] = 1

			else:
				self.flags = [0] * 8
				self.flags[7] = 1

		elif IR == ADD:
			self.registers[operand_a] += self.registers[operand_b]

		elif IR == AND:
			self.registers[operand_a] = self.registers[operand_a] & self.registers[operand_b]

		elif IR == DIV:
			if self.registers[operand_b] == 0:
				print('ERROR: Cannot Divide by Zero')
				sys.exit()

			else:
				self.registers[operand_a] /= self.registers[operand_b]

		else:
			raise Exception("Unsupported ALU operation")

	def trace(self):
		"""
		Handy function to print out the CPU state. You might want to call this
		from run() if you need help debugging.
		"""

		print(f"TRACE: %02X | %02X %02X %02X |" % (
			self.pc,
			#self.fl,
			#self.ie,
			self.ram_read(self.pc),
			self.ram_read(self.pc + 1),
			self.ram_read(self.pc + 2)
		), end='')

		for i in range(8):
			print(" %02X" % self.reg[i], end='')

		print()

	def run(self):
		"""Run the CPU."""

		self.running = True

		while self.running:
			#instruction register
			IR = self.ram_read(self.pc)

			operand_a = self.ram_read(self.pc + 1)

			operand_b = self.ram_read(self.pc + 2)

			num_operands = IR >> 6

			self.pc += 1 + num_operands

			is_alu_op = ((IR >> 5) & 0b001) == 1

			if is_alu_op:
				self.alu(IR, operand_a, operand_b)

			else:
				self.branch_table[IR](operand_a, operand_b)

	def hlt(self, operand_a, operand_b):
		self.running = False

	def ldi(self, operand_a, operand_b):
		self.registers[operand_a] = operand_b

	def prn(self, operand_a, operand_b):
		print(self.registers[operand_a])

	def push(self, operand_a, operand_b):
		#decrement stack pointer(SP)
		self.registers[7] -= 1

		#get value from register
		value = self.registers[operand_a]

		#put on the stack at SP
		SP = self.registers[7]
		self.ram_write(SP, value)

	def pop(self, operand_a, operand_b):
		#get value from stack
		SP = self.registers[7]
		value = self.ram_read(SP)

		#put value into register, indicated by operand_a
		self.registers[operand_a] = value

		#increment stack pointer
		self.registers[7] += 1

	def jeq(self, operand_a, operand_b):
		#if equal flag is true, jump to address in given register
		if self.flags[7] == 1:
			self.pc = self.registers[operand_a]

	def jne(self, operand_a, operand_b):
		#if equal flag is false, jump to address in given register
		if self.flags[7] == 0:
			self.pc = self.registers[operand_a]

	def jmp(self, operand_a, operand_b):
		#jump to address stored in given register
		#set pc to the address stored in given register
		self.pc = self.registers[operand_a]










