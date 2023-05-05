import unittest

from architecture_simulator.uarch.architectural_state import RegisterFile
from architecture_simulator.isa.rv32i_instructions import ADD, SUB, CSRRW, CSRRS, CSRRC, CSRRWI, CSRRSI, CSRRCI
from architecture_simulator.uarch.architectural_state import ArchitecturalState

from architecture_simulator.isa.parser import riscv_bnf, riscv_parser

import fixedint


class TestInstructions(unittest.TestCase):
    def test_add(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 5, 9, 0]))
        add_1 = ADD(rs1=1, rs2=2, rd=0)
        state = add_1.behavior(state)
        self.assertEqual(state.register_file.registers, [14, 5, 9, 0])

    def test_sub(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 5, 9, 0]))
        sub_1 = SUB(rs1=1, rs2=2, rd=0)
        state = sub_1.behavior(state)
        self.assertEqual(state.register_file.registers, [-4, 5, 9, 0])
     
""""   
    def test_csrrw_privilege_level_too_low(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        cssrw_1 = CSRRW(csr = 0, rs1 = 1, rd = 0)
        state.csr_registers.privilege_level = 0
        state.csr_registers.memory_file[3000] = 3
        self.assertRaises("illegal action: privilege level too low to access this csr register", cssrw_1.behavior(state))
        
    def test_csrrw_attempting_to_write_to_read_only(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        cssrw_1 = CSRRW(csr = 3072, rs1 = 1, rd = 0)
        state.csr_registers.memory_file[3072] = 3
        self.assertRaises("illegal action: attempting to write into read-only csr register", cssrw_1.behavior(state))
        
    def test_csrrw_invalid_adress(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        cssrw_1 = CSRRW(csr = 5000, rs1 = 1, rd = 0)
        state.csr_registers.memory_file[5000] = 3
        self.assertRaises("illegal action: csr register does not exist", cssrw_1.behavior(state))
    
    def test_csrrw(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        cssrw_1 = CSRRW(csr = 3000, rs1 = 1, rd = 0)
        state.csr_registers.memory_file[3000] = 3
        state.csr_registers.privilege_level = 4
        state = cssrw_1.behavior(state)
        self.assertEqual(state.register_file.registers, [3, 2])
        self.assertEqual(state.csr_registers[cssrw_1.csr], 2)
        
    def test_csrrs(self):
        max_number = fixedint.MutableUInt32(4294967295) #FF FF FF FF
        test_number_1 = fixedint.MutableUInt32(4294967294) #FF FF FF FE
        test_mask_1 = fixedint.MutableUInt32(1) # 00 00 00 01
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, test_mask_1]))
        state.csr_registers.memory_file[0] = test_number_1
        cssrs_1 = CSRRS(csr = 0, rs1 = 1, rd = 0)
        state = cssrs_1.behavior(state)
        self.assertEqual(state.register_file.registers, [test_number_1, test_mask_1])
        self.assertEqual(state.csr_registers[cssrs_1.csr], max_number)
        
    def test_csrrc(self):
        max_number = fixedint.MutableUInt32(4294967295) #FF FF FF FF
        test_result_1 = fixedint.MutableUInt32(1) # 00 00 00 01
        test_mask_1 = fixedint.MutableUInt32(4294967294) #FF FF FF FE
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, test_mask_1]))
        state.csr_registers.memory_file[0] = max_number
        cssrc_1 = CSRRC(csr = 0, rs1 = 1, rd = 0)
        state = cssrc_1.behavior(state)
        self.assertEqual(state.register_file.registers, [max_number, test_mask_1])
        self.assertEqual(state.csr_registers[cssrc_1.csr], test_result_1)
        
    def test_csrrwi(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 1]))
        state.csr_registers.memory_file[0] = 3
        cssrwi_1 = CSRRWI(csr = 0, uimm = 4, rd = 0)
        state = cssrwi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [3])
        self.assertEqual(state.csr_registers[cssrwi_1.csr], 4)
        
    def test_csrrsi(self):
        max_number = fixedint.MutableUInt32(4294967295) #FF FF FF FF
        test_number_1 = fixedint.MutableUInt32(4294967294) #FF FF FF FE
        test_mask_1 = fixedint.MutableUInt32(1) # 00 00 00 01
        state = ArchitecturalState(register_file=RegisterFile(registers=[0]))
        cssrsi_1 = CSRRSI(csr = 0, uimm = test_mask_1, rd = 0)
        state.csr_registers.memory_file[0] = test_number_1
        state = cssrsi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [test_number_1])
        self.assertEqual(state.csr_registers[cssrsi_1.csr], max_number)
        
    def test_csrrci(self):
        max_number = fixedint.MutableUInt32(4294967295) #FF FF FF FF
        test_result_1 = fixedint.MutableUInt32(1) # 00 00 00 01
        test_mask_1 = fixedint.MutableUInt32(4294967294) #FF FF FF FE
        state = ArchitecturalState(register_file=RegisterFile(registers=[0]))
        state.csr_registers.memory_file[0] = max_number
        cssrci_1 = CSRRCI(csr = 0, uimm = test_mask_1, rd = 0)
        state = cssrci_1.behavior(state)
        self.assertEqual(state.register_file.registers, [max_number])
        self.assertEqual(state.csr_registers[cssrci_1.csr], test_result_1)
"""


class TestParser(unittest.TestCase):
    program = """
add x0,x1,x2

# foo
# sub x1, x2, x4
"""
    expected = [
        ["add", ["x", "0"], ["x", "1"], ["x", "2"]],
        # ["sub", ["x", "1"], ["x", "2"], ["x", "4"]],
    ]

    def test_bnf(self):
        instr = riscv_bnf().parse_string(self.program)
        self.assertEqual(instr.as_list(), self.expected)
        self.assertNotEqual(instr[0].mnemonic, "")
        # self.assertEqual(instr[1].mnemonic, "")

    def test_parser(self):
        instr = riscv_parser(self.program)
        self.assertIsInstance(instr[0], ADD)
        self.assertEqual(instr[0].rd, 0)
        self.assertEqual(instr[0].rs1, 1)
        self.assertEqual(instr[0].rs2, 2)
        # self.assertIsInstance(instr[1], SUB)
        # self.assertEqual(instr[1].rd, 1)
        # self.assertEqual(instr[1].rs1, 2)
        # self.assertEqual(instr[1].rs2, 4)
