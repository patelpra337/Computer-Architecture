"""CPU functionality."""

import sys

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

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010,  # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111,  # PRN R0
            0b00000000,
            0b00000001,  # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

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

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            # Fetch the next instruction
            self.ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # Decode instruction
            binary_ir = bin(self.ir)[2:].zfill(8)
            operand_count = int(binary_ir[:2], 2)
            is_ALU_operation = binary_ir[2] == '1'
            instruction_does_set_pc = binary_ir[3] == '1'
            instruction_id = int(binary_ir[4:], 2)

            # Increment the program counter
            self.pc += (1 + operand_count)

            # Execute instruction
            if self.ir == int('00000001', 2):  # HLT
                running = False
            elif self.ir == int('10000010', 2):  # LDI
                self.reg[operand_a] = operand_b
            elif self.ir == int('01000111', 2):  # PRN
                print(self.reg[operand_a])
            else:
                print(
                    f"Error: Could not execute instruction: {bin(self.ir)[2:].zfill(8)}")
                sys.exit(1)