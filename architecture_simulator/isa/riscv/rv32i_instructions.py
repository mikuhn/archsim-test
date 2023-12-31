from __future__ import annotations
from typing import Optional, Type, TYPE_CHECKING
from dataclasses import dataclass
import fixedint

from architecture_simulator.uarch.riscv.control_unit_signals import ControlUnitSignals
from .instruction_types import (
    RiscvInstruction,
    RTypeInstruction,
    ITypeInstruction,
    ShiftITypeInstruction,
    MemoryITypeInstruction,
    STypeInstruction,
    BTypeInstruction,
    UTypeInstruction,
    JTypeInstruction,
    FenceTypeInstruction,
    CSRTypeInstruction,
    CSRITypeInstruction,
)

if TYPE_CHECKING:
    from architecture_simulator.uarch.riscv.riscv_architectural_state import (
        RiscvArchitecturalState,
    )


@dataclass
class InstructionNotImplemented(NotImplementedError):
    mnemonic: str

    def __repr__(self):
        return f"Instruction {self.mnemonic} is not yet implemented"


class ADD(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="add")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Addition:
            rd = rs1 + rs2

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 + rs2
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = fixedint.MutableUInt32(alu_in_2)
        result = int(left + right)
        return (None, result)


class SUB(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="sub")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Subtraction:
            rd = rs1 - rs2

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(fixedint.Int32(int(rs1)) - fixedint.Int32(int(rs2)))
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = fixedint.MutableUInt32(alu_in_2)
        result = int(fixedint.Int32(int(left)) - fixedint.Int32(int(right)))
        return (None, result)


class SLL(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="sll")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Shift left logical:
            rd = rs1 << rs2

        (shift amount determined by lower 5 bits of rs2)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[
            self.rs2
        ] % fixedint.MutableUInt32(32)
        architectural_state.register_file.registers[self.rd] = rs1 << rs2
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = fixedint.MutableUInt32(alu_in_2) % fixedint.MutableUInt32(32)
        result = int(left << right)
        return (None, result)


class SLT(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="slt")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Set lower than:
            rd = 1 if (rs1 < rs2) else 0

        (register values are interpreted as signed integers)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        rs2 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs2]))
        architectural_state.register_file.registers[self.rd] = (
            fixedint.MutableUInt32(1) if rs1 < rs2 else fixedint.MutableUInt32(0)
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.Int32(alu_in_1)
        right = fixedint.Int32(alu_in_2)
        result = 1 if left < right else 0
        return (None, result)


class SLTU(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="sltu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Set lower than unsigned:
            rd = 1 if (rs1 < rs2) else 0

        (register values are interpreted as unsigned integers)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = (
            fixedint.MutableUInt32(1) if rs1 < rs2 else fixedint.MutableUInt32(0)
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = 1 if left < right else 0
        return (None, result)


class XOR(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="xor")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        XOR:
            rd = rs1 ^ rs2

        (executed bitwise)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 ^ rs2
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = fixedint.MutableUInt32(alu_in_2)
        result = int(left ^ right)
        return (None, result)


class SRL(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="srl")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Shift right logical:
            rd = rs1 >> rs2

        (shift amount determined by lower 5 bits of rs2)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[
            self.rs2
        ] % fixedint.MutableUInt32(32)
        architectural_state.register_file.registers[self.rd] = rs1 >> rs2
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = fixedint.MutableUInt32(alu_in_2) % fixedint.MutableUInt32(32)
        result = int(left >> right)
        return (None, result)


class SRA(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="sra")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Shift right arithmetic:
            rd = rs1 >>s rs2

        (shift amount determined by lower 5 bits of rs2)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        rs2 = fixedint.Int32(
            int(
                architectural_state.register_file.registers[self.rs2]
                % fixedint.MutableUInt32(32)
            )
        )
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(rs1 >> rs2)
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.Int32(alu_in_1)
        right = fixedint.Int32(
            int(fixedint.UInt32(alu_in_2) % fixedint.MutableUInt32(32))
        )
        result = int(left >> right)
        return (None, result)


class OR(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="or")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        OR:
            rd = rs1 | rs2

        (executed bitwise)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 | rs2
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = fixedint.MutableUInt32(alu_in_2)
        result = int(left | right)
        return (None, result)


class AND(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="and")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        AND:
            rd = rs1 & rs2

        (executed bitwise)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 & rs2
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = fixedint.MutableUInt32(alu_in_2)
        result = int(left & right)
        return (None, result)


class ADDI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="addi")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] + sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = rs1 + fixedint.MutableUInt32(self.imm)
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = fixedint.MutableUInt32(alu_in_2)
        result = int(left + right)
        return (None, result)


class SLTI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="slti")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] <s sext(imm)"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = (
            fixedint.MutableUInt32(1)
            if rs1 < fixedint.Int32(self.imm)
            else fixedint.MutableUInt32(0)
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.Int32(alu_in_1)
        right = fixedint.Int32(alu_in_2)
        result = 1 if left < right else 0
        return (None, result)


class SLTIU(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="sltiu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] <u sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = (
            fixedint.MutableUInt32(1)
            if rs1 < fixedint.MutableUInt32(self.imm)
            else fixedint.MutableUInt32(0)
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = 1 if left < right else 0
        return (None, result)


class XORI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="xori")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] ^ sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = rs1 ^ fixedint.MutableUInt32(self.imm)
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = fixedint.MutableUInt32(alu_in_2)
        result = int(left ^ right)
        return (None, result)


class ORI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="ori")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] | sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = rs1 | fixedint.MutableUInt32(self.imm)
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = fixedint.MutableUInt32(alu_in_2)
        result = int(left | right)
        return (None, result)


class ANDI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="andi")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] & sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = rs1 & fixedint.MutableUInt32(self.imm)
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = fixedint.MutableUInt32(alu_in_2)
        result = int(left & right)
        return (None, result)


class SLLI(ShiftITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="slli")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] << shamt  (imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = rs1 << fixedint.MutableUInt32(self.imm)
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = fixedint.MutableUInt32(alu_in_2)
        result = int(left << right)
        return (None, result)


class SRLI(ShiftITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="srli")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] >>u shamt  (imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = rs1 >> fixedint.MutableUInt32(self.imm)
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = fixedint.MutableUInt32(alu_in_2)
        result = int(left >> right)
        return (None, result)


class SRAI(ShiftITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="srai")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] >>s shamt   (imm)"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            rs1 >> int(fixedint.UInt16(self.imm))
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.Int32(alu_in_1)
        right = alu_in_2
        result = int(left >> right)
        return (None, result)


class LB(MemoryITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lb")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = sext(M[x[rs1] + sext(imm)][7:0])"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        # casting like this is necessary for sign extension
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(
                fixedint.Int8(
                    int(architectural_state.memory.read_byte(int(rs1) + self.imm))
                )
            )
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = alu_in_2
        result = int(left) + right
        return (None, result)

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
    ) -> Optional[int]:
        assert memory_address is not None
        return int(
            fixedint.Int8(int(architectural_state.memory.read_byte(memory_address)))
        )


class LH(MemoryITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lh")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = sext(M[x[rs1] + sext(imm)][15:0])"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(
                fixedint.Int16(
                    int(architectural_state.memory.read_halfword(int(rs1) + self.imm))
                )
            )
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = alu_in_2
        result = int(left) + right
        return (None, result)

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
    ) -> Optional[int]:
        assert memory_address is not None
        return int(
            fixedint.Int16(
                int(architectural_state.memory.read_halfword(memory_address))
            )
        )


class LW(MemoryITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lw")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = sext(M[x[rs1] + sext(imm)][31:0])"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.memory.read_word(int(rs1) + self.imm)
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = alu_in_2
        result = int(left) + right
        return (None, result)

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
    ) -> Optional[int]:
        assert memory_address is not None
        return int(architectural_state.memory.read_word(memory_address))


class LBU(MemoryITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lbu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = M[x[rs1] + sext(imm)][7:0]"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(architectural_state.memory.read_byte(int(rs1) + self.imm))
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = alu_in_2
        result = int(left) + right
        return (None, result)

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
    ) -> Optional[int]:
        assert memory_address is not None
        return int(architectural_state.memory.read_byte(memory_address))


class LHU(MemoryITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lhu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = M[x[rs1] + sext(imm)][15:0]"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(architectural_state.memory.read_halfword(int(rs1) + self.imm))
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.MutableUInt32(alu_in_1)
        right = alu_in_2
        result = int(left) + right
        return (None, result)

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
    ) -> Optional[int]:
        assert memory_address is not None
        return int(architectural_state.memory.read_halfword(memory_address))


class JALR(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="jalr")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """t=pc+4; pc=(x[rs1]+sext(imm))&∼1; x[rd]=t"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            architectural_state.program_counter + 4
        )
        architectural_state.program_counter = (
            int((rs1 + fixedint.Int16(self.imm))) & (pow(2, 32) - 2)
        ) - self.length
        return architectural_state

    def control_unit_signals(self) -> ControlUnitSignals:
        return ControlUnitSignals(
            alu_src_1=True,
            alu_src_2=True,
            wb_src=0,
            reg_write=True,
            mem_read=False,
            mem_write=False,
            branch=False,
            jump=False,
            alu_op=None,
            alu_to_pc=True,
        )

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        return None, ((alu_in_1 + alu_in_2) & (~1))


class ECALL(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="ecall")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """RaiseException(EnvironmentCall)"""
        raise InstructionNotImplemented(mnemonic=self.mnemonic)
        return architectural_state

    def __repr__(self) -> str:
        return self.mnemonic


class EBREAK(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="ebreak")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """RaiseException(EnvironmentCall)"""
        raise InstructionNotImplemented(mnemonic=self.mnemonic)
        return architectural_state

    def __repr__(self) -> str:
        return self.mnemonic


class SB(STypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1, rs2, imm, mnemonic="sb")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """M[x[rs1] + sext(imm)] = x[rs2][7:0]"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2][:8]
        architectural_state.memory.write_byte(
            int(rs1 + fixedint.MutableUInt32(self.imm)), fixedint.MutableUInt8(int(rs2))
        )
        return architectural_state

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
    ) -> Optional[int]:
        if memory_address is not None and memory_write_data is not None:
            architectural_state.memory.write_byte(
                memory_address, fixedint.MutableUInt8(memory_write_data)
            )
        return None

    def access_register_file(
        self, architectural_state: RiscvArchitecturalState
    ) -> tuple[
        Optional[int], Optional[int], Optional[int], Optional[int], Optional[int]
    ]:
        return (
            self.rs1,
            self.rs2,
            int(architectural_state.register_file.registers[self.rs1]),
            int(architectural_state.register_file.registers[self.rs2][:8]),
            self.imm,
        )


class SH(STypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1, rs2, imm, mnemonic="sh")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """M[x[rs1] + sext(imm)] = x[rs2][15:0]"""
        rs2 = architectural_state.register_file.registers[self.rs2][:16]
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.memory.write_halfword(
            int(rs1 + fixedint.MutableUInt32(self.imm)),
            fixedint.MutableUInt16(int(rs2)),
        )
        return architectural_state

    def access_register_file(
        self, architectural_state: RiscvArchitecturalState
    ) -> tuple[
        Optional[int], Optional[int], Optional[int], Optional[int], Optional[int]
    ]:
        return (
            self.rs1,
            self.rs2,
            int(architectural_state.register_file.registers[self.rs1]),
            int(architectural_state.register_file.registers[self.rs2][:16]),
            self.imm,
        )

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
    ) -> Optional[int]:
        if memory_address is not None and memory_write_data is not None:
            architectural_state.memory.write_halfword(
                memory_address, fixedint.MutableUInt16(memory_write_data)
            )
        return None


class SW(STypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1, rs2, imm, mnemonic="sw")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """M[x[rs1] + sext(imm)] = x[rs2][31:0]"""
        rs2 = architectural_state.register_file.registers[self.rs2]
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.memory.write_word(
            int(rs1 + fixedint.MutableUInt32(self.imm)), rs2
        )
        return architectural_state

    def access_register_file(
        self, architectural_state: RiscvArchitecturalState
    ) -> tuple[
        Optional[int], Optional[int], Optional[int], Optional[int], Optional[int]
    ]:
        return (
            self.rs1,
            self.rs2,
            int(architectural_state.register_file.registers[self.rs1]),
            int(architectural_state.register_file.registers[self.rs2]),
            self.imm,
        )

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
    ) -> Optional[int]:
        if memory_address is not None and memory_write_data is not None:
            architectural_state.memory.write_word(
                memory_address, fixedint.MutableUInt32(memory_write_data)
            )
        return None


class BEQ(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="beq")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """if (x[rs1] == x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 == rs2:
            architectural_state.program_counter += self.imm - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        return (alu_in_1 == alu_in_2), None


class BNE(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bne")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """if (x[rs1] != x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 != rs2:
            architectural_state.program_counter += self.imm - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        return (alu_in_1 != alu_in_2), None


class BLT(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="blt")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """if (x[rs1] <s x[rs2]) pc += sext(imm)"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        rs2 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs2]))
        if rs1 < rs2:
            architectural_state.program_counter += self.imm - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        # casting for signed comparison (inputs are unsigned)
        return (fixedint.Int32(alu_in_1) < fixedint.Int32(alu_in_2)), None


class BGE(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bge")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """if (x[rs1] >= x[rs2]) pc += sext(imm)"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        rs2 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs2]))
        if rs1 >= rs2:
            architectural_state.program_counter += self.imm - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        # casting for signed comparison (inputs are unsigned)
        return (fixedint.Int32(alu_in_1) >= fixedint.Int32(alu_in_2)), None


class BLTU(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bltu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """if (x[rs1] <u x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 < rs2:
            architectural_state.program_counter += self.imm - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        return (alu_in_1 < alu_in_2), None


class BGEU(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bgeu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """if (x[rs1] >=u x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 >= rs2:
            architectural_state.program_counter += self.imm - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        return (alu_in_1 >= alu_in_2), None


class LUI(UTypeInstruction):
    def __init__(self, rd: int, imm: int):
        super().__init__(rd, imm, mnemonic="lui")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = sext(imm[31:12] << 12)"""
        imm = self.imm << 12
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            imm
        )
        return architectural_state

    def control_unit_signals(self) -> ControlUnitSignals:
        return ControlUnitSignals(
            alu_src_1=None,
            alu_src_2=None,
            wb_src=3,
            reg_write=True,
            mem_read=False,
            mem_write=False,
            branch=False,
            jump=False,
            alu_op=None,
            alu_to_pc=False,
        )


class AUIPC(UTypeInstruction):
    def __init__(self, rd: int, imm: int):
        super().__init__(rd, imm, mnemonic="auipc")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = pc + sext(imm[31:12] << 12)"""
        imm = self.imm << 12
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            architectural_state.program_counter + imm
        )
        return architectural_state

    def control_unit_signals(self) -> ControlUnitSignals:
        return ControlUnitSignals(
            alu_src_1=False,
            alu_src_2=True,
            wb_src=2,
            reg_write=True,
            mem_read=False,
            mem_write=False,
            branch=False,
            jump=False,
            alu_op=None,
            alu_to_pc=False,
        )

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        return None, (alu_in_1 + alu_in_2)


class JAL(JTypeInstruction):
    def __init__(self, rd: int, imm: int):
        super().__init__(rd, imm, mnemonic="jal")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        # NOTE: Actually sets the pc to (pc+imm-4) because the simulation always increases the pc by 4 after execution
        """x[rd]=pc+4; pc+=sext(imm)"""
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            architectural_state.program_counter + 4
        )
        architectural_state.program_counter += self.imm - self.length
        architectural_state.performance_metrics.procedure_count += 1
        return architectural_state


class FENCE(FenceTypeInstruction):
    def __init__(self):
        super().__init__(mnemonic="fence")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """fence(pred,succ)"""
        raise InstructionNotImplemented(mnemonic=self.mnemonic)


class CSRRW(CSRTypeInstruction):
    def __init__(self, rd: int, csr: int, rs1: int):
        super().__init__(rd, csr, rs1, mnemonic="csrrw")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = x[rs1]

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.read_word(self.csr)
        architectural_state.csr_registers.write_word(
            self.csr, architectural_state.register_file.registers[self.rs1]
        )

        return architectural_state


class CSRRS(CSRTypeInstruction):
    def __init__(self, rd: int, csr: int, rs1: int):
        super().__init__(rd, csr, rs1, mnemonic="csrrs")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = csr_register[csr] or x[rs1]

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        rs1_value = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.read_word(self.csr)
        temp = architectural_state.csr_registers.read_word(self.csr) | rs1_value
        architectural_state.csr_registers.write_word(self.csr, temp)

        return architectural_state


class CSRRC(CSRTypeInstruction):
    def __init__(self, rd: int, csr: int, rs1: int):
        super().__init__(rd, csr, rs1, mnemonic="csrrc")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = csr_register[csr] and not(x[rs1])

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        rs1_value = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.read_word(self.csr)
        temp = architectural_state.csr_registers.read_word(self.csr) & (~(rs1_value))
        architectural_state.csr_registers.write_word(self.csr, temp)

        return architectural_state


class CSRRWI(CSRITypeInstruction):
    def __init__(self, rd: int, csr: int, uimm: int):
        super().__init__(rd, csr, uimm, mnemonic="csrrwi")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = zext(uimm)

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.read_word(self.csr)
        architectural_state.csr_registers.write_word(
            self.csr, fixedint.MutableUInt32(self.uimm)
        )

        return architectural_state


class CSRRSI(CSRITypeInstruction):
    def __init__(self, rd: int, csr: int, uimm: int):
        super().__init__(rd, csr, uimm, mnemonic="csrrsi")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = csr_register[csr] or zext(uimm)

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.read_word(self.csr)
        temp = architectural_state.csr_registers.read_word(
            self.csr
        ) | fixedint.MutableUInt32(self.uimm)
        architectural_state.csr_registers.write_word(self.csr, temp)

        return architectural_state


class CSRRCI(CSRITypeInstruction):
    def __init__(self, rd: int, csr: int, uimm: int):
        super().__init__(rd, csr, uimm, mnemonic="csrrci")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = csr_register[csr] and not(zext(uimm))

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.read_word(self.csr)
        temp = architectural_state.csr_registers.read_word(self.csr) & (
            ~(fixedint.MutableUInt32(self.uimm))
        )
        architectural_state.csr_registers.write_word(self.csr, temp)

        return architectural_state


# Used by the parser to instantiate instructions.
instruction_map: dict[str, Type[RiscvInstruction]] = {
    "add": ADD,
    "beq": BEQ,
    "blt": BLT,
    "bne": BNE,
    "sub": SUB,
    "bge": BGE,
    "bltu": BLTU,
    "bgeu": BGEU,
    "csrrw": CSRRW,
    "csrrs": CSRRS,
    "csrrc": CSRRC,
    "csrrwi": CSRRWI,
    "csrrsi": CSRRSI,
    "csrrci": CSRRCI,
    "sb": SB,
    "sh": SH,
    "sw": SW,
    "lui": LUI,
    "auipc": AUIPC,
    "jal": JAL,
    "fence": FENCE,
    "sll": SLL,
    "slt": SLT,
    "sltu": SLTU,
    "xor": XOR,
    "srl": SRL,
    "sra": SRA,
    "or": OR,
    "and": AND,
    "lb": LB,
    "lh": LH,
    "lw": LW,
    "lbu": LBU,
    "lhu": LHU,
    "srai": SRAI,
    "jalr": JALR,
    "ecall": ECALL,
    "ebreak": EBREAK,
    "addi": ADDI,
    "slti": SLTI,
    "sltiu": SLTIU,
    "xori": XORI,
    "ori": ORI,
    "andi": ANDI,
    "slli": SLLI,
    "srli": SRLI,
}
