import unittest
import fixedint

from architecture_simulator.uarch.architectural_state import (
    RegisterFile,
    Memory,
    InstructionMemory,
    ArchitecturalState,
    MemoryAddressError,
)
from architecture_simulator.simulation.simulation import (
    Simulation,
    InstructionExecutionException,
)
from architecture_simulator.isa.rv32i_instructions import ADDI, BNE, BEQ, JAL, LW


class TestSimulation(unittest.TestCase):
    def test_simulation(self):
        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0, 2, 0, 0]),
                memory=Memory(memory_file=()),
            )
        )
        simulation.state.instruction_memory.append_instructions(
            "add x0, x0, x1\nadd x0, x0, x1"
        )
        # simulation.append_instructions("sub x0, x0, x1")
        simulation.step_simulation()
        self.assertEqual(simulation.state.register_file.registers[0], 2)
        simulation.step_simulation()
        self.assertEqual(simulation.state.register_file.registers[0], 4)
        # simulation.step_simulation()
        # self.assertEqual(simulation.state.register_file.registers[0], 2)

    # testing whether the addresses for the instructions get computed correctly
    def test_append_multiple_instructions(self):
        simulation = Simulation(state=ArchitecturalState(register_file=RegisterFile()))
        simulation.state.instruction_memory.append_instructions("addi x1, x0, 12")
        simulation.state.instruction_memory.append_instructions("bne x7, x7, 30")
        simulation.state.instruction_memory.append_instructions("jal x12, 30")
        self.assertEqual(
            simulation.state.instruction_memory.instructions,
            {
                0: ADDI(rd=1, rs1=0, imm=12),
                4: BNE(rs1=7, rs2=7, imm=30),
                8: JAL(rd=12, imm=30),
            },
        )

    def test_run_simulation(self):
        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0]),
                instruction_memory=InstructionMemory(
                    instructions={
                        0: ADDI(rd=1, rs1=1, imm=1),
                        4: ADDI(rd=1, rs1=1, imm=1),
                        8: ADDI(rd=1, rs1=1, imm=1),
                        12: ADDI(rd=1, rs1=1, imm=1),
                        16: ADDI(rd=1, rs1=1, imm=1),
                        20: ADDI(rd=1, rs1=1, imm=1),
                        24: ADDI(rd=1, rs1=1, imm=1),
                    },
                ),
            ),
        )
        simulation.run_simulation()
        self.assertEqual(int(simulation.state.register_file.registers[1]), 7)
        self.assertEqual(simulation.state.performance_metrics.branch_count, 0)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 7)
        self.assertEqual(simulation.state.performance_metrics.procedure_count, 0)
        self.assertGreater(
            simulation.state.performance_metrics.instructions_per_second, 0
        )
        self.assertGreater(simulation.state.performance_metrics.execution_time_s, 0)

        simulation = Simulation(
            state=ArchitecturalState(register_file=RegisterFile(registers=[0, 0, 0, 0]))
        )

        simulation.run_simulation()
        self.assertEqual(int(simulation.state.register_file.registers[0]), 0)
        self.assertEqual(simulation.state.performance_metrics.branch_count, 0)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 0)
        self.assertEqual(simulation.state.performance_metrics.procedure_count, 0)
        self.assertEqual(
            simulation.state.performance_metrics.instructions_per_second, 0
        )
        self.assertGreaterEqual(
            simulation.state.performance_metrics.execution_time_s, 0
        )

        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0]),
                instruction_memory=InstructionMemory(
                    instructions={
                        0: ADDI(rd=2, rs1=0, imm=5),
                        4: ADDI(rd=1, rs1=1, imm=1),
                        8: BNE(rs1=1, rs2=2, imm=-2),
                        12: BEQ(rs1=0, rs2=0, imm=4),
                        16: ADDI(rd=0, rs1=0, imm=0),
                        20: ADDI(rd=3, rs1=0, imm=64),
                    },
                ),
            ),
        )
        simulation.run_simulation()
        self.assertEqual(simulation.state.register_file.registers, [0, 5, 5, 64])
        self.assertEqual(simulation.state.performance_metrics.branch_count, 5)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 13)
        self.assertEqual(simulation.state.performance_metrics.procedure_count, 0)
        self.assertGreater(
            simulation.state.performance_metrics.instructions_per_second, 0
        )
        self.assertGreater(simulation.state.performance_metrics.execution_time_s, 0)

        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0]),
                instruction_memory=InstructionMemory(
                    instructions={
                        0: ADDI(rd=2, rs1=0, imm=33),
                        4: ADDI(rd=1, rs1=1, imm=1),
                        8: ADDI(rd=1, rs1=1, imm=1),
                        12: ADDI(rd=1, rs1=1, imm=1),
                        16: BNE(rs1=1, rs2=2, imm=-6),
                    },
                ),
            ),
        )
        simulation.run_simulation()
        self.assertEqual(simulation.state.register_file.registers, [0, 33, 33, 0])
        self.assertEqual(simulation.state.performance_metrics.branch_count, 10)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 45)
        self.assertEqual(simulation.state.performance_metrics.procedure_count, 0)
        self.assertGreater(
            simulation.state.performance_metrics.instructions_per_second, 0
        )
        self.assertGreater(simulation.state.performance_metrics.execution_time_s, 0)

        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0]),
                instruction_memory=InstructionMemory(
                    instructions={
                        0: ADDI(rd=3, rs1=0, imm=8),
                        4: JAL(rd=2, imm=4),
                        8: ADDI(rd=1, rs1=1, imm=1),
                        12: BEQ(rs1=0, rs2=0, imm=2),
                        16: JAL(rd=2, imm=2),
                        20: ADDI(rd=1, rs1=1, imm=-10),
                    },
                ),
            )
        )
        simulation.run_simulation()
        self.assertEqual(
            simulation.state.register_file.registers, [0, pow(2, 32) - 10, 20, 8]
        )
        self.assertEqual(simulation.state.performance_metrics.branch_count, 1)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 5)
        self.assertEqual(simulation.state.performance_metrics.procedure_count, 2)
        self.assertGreater(
            simulation.state.performance_metrics.instructions_per_second, 0
        )
        self.assertGreater(simulation.state.performance_metrics.execution_time_s, 0)

    def test_against_class_variables(self):
        """Some tests against class variables (some things used to be class variables and were thus shared between objects, which was undesired)"""
        simulation1 = Simulation(state=ArchitecturalState(memory=Memory(min_bytes=0)))
        simulation2 = Simulation(state=ArchitecturalState(memory=Memory(min_bytes=0)))

        simulation1.state.register_file.registers[5] = fixedint.MutableUInt32(12)
        self.assertEqual(int(simulation1.state.register_file.registers[5]), 12)
        self.assertEqual(int(simulation2.state.register_file.registers[5]), 0)

        simulation1.state.instruction_memory.instructions = {
            0: ADDI(rd=5, rs1=12, imm=12)
        }
        self.assertEqual(len(simulation1.state.instruction_memory.instructions), 1)
        self.assertEqual(len(simulation2.state.instruction_memory.instructions), 0)

        simulation1.state.csr_registers.store_byte(
            address=5, value=fixedint.MutableUInt8(12)
        )
        self.assertEqual(
            (int(simulation1.state.csr_registers.load_byte(address=5))), 12
        )
        self.assertEqual((int(simulation2.state.csr_registers.load_byte(address=5))), 0)

        simulation1.state.performance_metrics.instruction_count = 12
        self.assertEqual(simulation1.state.performance_metrics.instruction_count, 12)
        self.assertEqual(simulation2.state.performance_metrics.instruction_count, 0)

        simulation1.state.memory.store_byte(address=5, value=fixedint.MutableUInt8(12))
        self.assertEqual(int(simulation1.state.memory.load_byte(address=5)), 12)
        self.assertEqual(int(simulation2.state.memory.load_byte(address=5)), 0)

    def test_step_simulation_over(self):
        simulation = Simulation()
        simulation.state.instruction_memory.instructions = {
            0: ADDI(rd=1, rs1=1, imm=1),
            4: ADDI(rd=1, rs1=1, imm=1),
            8: ADDI(rd=1, rs1=1, imm=1),
            12: ADDI(rd=1, rs1=1, imm=1),
        }

        self.assert_(simulation.step_simulation())
        self.assert_(simulation.step_simulation())
        self.assert_(simulation.step_simulation())
        self.assert_(not simulation.step_simulation())

    def test_simulation_errors(self):
        simulation = Simulation()
        simulation.state.instruction_memory.instructions = {
            0: ADDI(rd=1, rs1=1, imm=1),
            4: LW(rd=1, rs1=0, imm=0),
        }

        with self.assertRaises(InstructionExecutionException) as cm:
            simulation.run_simulation()
        self.assertEqual(
            cm.exception.__repr__(),
            InstructionExecutionException(
                address=4,
                instruction_repr=simulation.state.instruction_memory.instructions[4],
                error_message=MemoryAddressError(
                    address=0,
                    min_address_incl=2**14,
                    max_address_incl=2**32 - 1,
                    memory_type="data memory",
                ).__repr__(),
            ).__repr__(),
        )
