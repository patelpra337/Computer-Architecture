"""CPU functionality."""

import sys
import os.path

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256

        self.reg = [0] * 8

        # Internal Registers
        self.pc = 0
        self.ir = 0
        self.mar = 0
        self.mdr = 0
        self.fl = 0
        self.halted = False

        self.reg[7] = 0xF4
    
        # Setup Branch Table
        self.branchtable = {}
        self.branchtable[HLT] = self.execute_HLT
        self.branchtable[LDI] = self.execute_LDI
        self.branchtable[PRN] = self.execute_PRN
        self.branchtable[MUL] = self.execute_MUL
        self.branchtable[PUSH] = self.execute_PUSH
        self.branchtable[POP] = self.execute_POP

    # Property wrapper for SP (Stack Pointer)
    @property
    def sp(self):
        return self.reg[7]

    @sp.setter
    def sp(self, a):
        self.reg[7] = a & 0xFF

    def instruction_size(self):
        return ((self.ir >> 6) & 0b11) + 1

    def instruction_sets_pc(self):
        return ((self.ir >> 4) & 0b0001) == 1

    def ram_read(self, mar):
        if mar >= 0 and mar < len(self.ram):
            return self.ram[mar]
        else:
            print(
                f"Error: Attempted to read from memory address: {mar}, which is outside of the memory bounds.")
            return -1

    def ram_write(self, mar, mdr):
        if mar >= 0 and mar < len(self.ram):
            self.ram[mar] = mdr & 0xFF
        else:
            print(
                f"Error: Attempted to write to memory address: {mar}, which is outside of the memory bounds.")

    def load(self, file_name):
        """Load a program into memory."""
        address = 0

        file_path = os.path.join(os.path.dirname(__file__), file_name)
        try:
            with open(file_path) as f:
                for line in f:
                    num = line.split("#")[0].strip()  # "10000010"
                    try:
                        instruction = int(num, 2)
                        self.ram[address] = instruction
                        address += 1
                    except:
                        continue
        except:
            print(f'Could not find file named: {file_name}')
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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

    # Run Loop

    def run(self):
        """Run the CPU."""
        while not self.halted:
            self.ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if not self.instruction_sets_pc():
                self.pc += self.instruction_size()

            self.execute_instruction(operand_a, operand_b)

    def execute_instruction(self, operand_a, operand_b):
        if self.ir in self.branchtable:
            self.branchtable[self.ir](operand_a, operand_b)
        else:
            print(
                f"Error: Could not find instruction: {self.ir} in branch table.")
            sys.exit(1)
