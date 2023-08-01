from __future__ import annotations
from typing import TYPE_CHECKING, Type
from fixedint import MutableUInt16
from ..instruction import Instruction

if TYPE_CHECKING:
    from architecture_simulator.uarch.toy.toy_architectural_state import (
        ToyArchitecturalState,
    )


class ToyInstruction(Instruction):
    length: int = 1

    def __init__(self, **kwargs):
        self.mnemonic = kwargs["mnemonic"].upper()
        self.opcode = kwargs["opcode"] % 16

    def __repr__(self):
        return self.mnemonic

    def behavior(self, state: ToyArchitecturalState):
        pass

    def __eq__(self, other):
        return self.opcode == other.opcode


class AddressTypeInstruction(ToyInstruction):
    def __init__(self, address: int, **kwargs):
        super().__init__(**kwargs)
        self.address = address % 4096

    def __repr__(self):
        return f"{self.mnemonic} ${self.address:03x}"

    def __eq__(self, other):
        return super().__eq__(other) and self.address == other.address


class STO(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="STO", opcode=0, address=address)

    def behavior(self, state: ToyArchitecturalState):
        # NOTE: The Memory class is byte addressed, but the toy architecture uses a halfword addressed memory.
        # Thus, we need to shift the address by one bit
        state.data_memory.store_halfword(address=self.address, value=state.accu)
        state.increment_pc()


class LDA(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="LDA", opcode=1, address=address)

    def behavior(self, state: ToyArchitecturalState):
        # NOTE: The Memory class is byte addressed, but the toy architecture uses a halfword addressed memory.
        # Thus, we need to shift the address by one bit
        state.accu = state.data_memory.load_halfword(address=self.address)
        state.increment_pc()


class BRZ(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="BRZ", opcode=2, address=address)

    def behavior(self, state: ToyArchitecturalState):
        if state.accu:
            state.increment_pc()
        else:
            # NOTE: sets the pc to self.address without additionally increasing the program counter.
            # If instructions should ever get saved in a unified memory and are thus editable by other instructions,
            # this needs to change or you need to address this during parsing
            state.program_counter = MutableUInt16(self.address)


class ADD(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="ADD", opcode=3, address=address)

    def behavior(self, state: ToyArchitecturalState):
        memory = state.data_memory.load_halfword(address=self.address)
        state.accu = state.accu + memory
        state.increment_pc()


class SUB(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="SUB", opcode=4, address=address)

    def behavior(self, state: ToyArchitecturalState):
        memory = state.data_memory.load_halfword(address=self.address)
        state.accu = state.accu - memory
        state.increment_pc()


class OR(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="OR", opcode=5, address=address)

    def behavior(self, state: ToyArchitecturalState):
        memory = state.data_memory.load_halfword(address=self.address)
        state.accu = state.accu | memory
        state.increment_pc()


class AND(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="AND", opcode=6, address=address)

    def behavior(self, state: ToyArchitecturalState):
        memory = state.data_memory.load_halfword(address=self.address)
        state.accu = state.accu & memory
        state.increment_pc()


class XOR(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="XOR", opcode=7, address=address)

    def behavior(self, state: ToyArchitecturalState):
        memory = state.data_memory.load_halfword(address=self.address)
        state.accu = state.accu ^ memory
        state.increment_pc()


class NOT(ToyInstruction):
    def __init__(self):
        super().__init__(mnemonic="NOT", opcode=8)

    def behavior(self, state: ToyArchitecturalState):
        state.accu = ~state.accu
        state.increment_pc()


class INC(ToyInstruction):
    def __init__(self):
        super().__init__(mnemonic="INC", opcode=9)

    def behavior(self, state: ToyArchitecturalState):
        state.accu += MutableUInt16(1)
        state.increment_pc()


class DEC(ToyInstruction):
    def __init__(self):
        super().__init__(mnemonic="DEC", opcode=10)

    def behavior(self, state: ToyArchitecturalState):
        state.accu -= MutableUInt16(1)
        state.increment_pc()


class ZRO(ToyInstruction):
    def __init__(self) -> None:
        super().__init__(mnemonic="ZRO", opcode=11)

    def behavior(self, state: ToyArchitecturalState):
        state.accu = MutableUInt16(0)
        state.increment_pc()


class NOP(ToyInstruction):
    def __init__(self) -> None:
        super().__init__(mnemonic="NOP", opcode=12)

    def behavior(self, state: ToyArchitecturalState):
        state.increment_pc()


instruction_map: dict[str, Type[ToyInstruction]] = {
    "STO": STO,
    "LDA": LDA,
    "BRZ": BRZ,
    "ADD": ADD,
    "SUB": SUB,
    "OR": OR,
    "AND": AND,
    "XOR": XOR,
    "NOT": NOT,
    "INC": INC,
    "DEC": DEC,
    "ZRO": ZRO,
    "NOP": NOP,
}
