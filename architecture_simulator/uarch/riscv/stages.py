from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .pipeline_registers import (
    PipelineRegister,
    InstructionFetchPipelineRegister,
    InstructionDecodePipelineRegister,
    ExecutePipelineRegister,
    MemoryAccessPipelineRegister,
    RegisterWritebackPipelineRegister,
)

from architecture_simulator.isa.riscv.instruction_types import (
    BTypeInstruction,
    EmptyInstruction,
)
from architecture_simulator.isa.riscv.rv32i_instructions import JAL
from .pipeline import InstructionExecutionException

if TYPE_CHECKING:
    from architecture_simulator.uarch.riscv.riscv_architectural_state import (
        RiscvArchitecturalState,
    )


class Stage:
    """Stage superclass. Every stage needs to implement a behavior method"""

    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """general behavior method

        Args:
            pipeline_register (PipelineRegister): gets the data from the stage before as argument
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns data of this stage
        """
        return PipelineRegister()


class InstructionFetchStage(Stage):
    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """behavior of the IF Stage
        The input pipeline_register can be of any type of PipelineRegister

        Args:
            pipeline_register (PipelineRegister): gets a PipelineRegister as argument, but does not use it
            (it only gets this to be consistent with the superclass)
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns the InstructionFetchPipelineRegister class with all information from the
            IF stage
        """
        if not state.instruction_at_pc():
            return InstructionFetchPipelineRegister()
        # NOTE: PC gets incremented here. This means that branch prediction also happens here. Currently, we just statically predict not taken.
        address_of_instruction = state.program_counter
        instruction = state.instruction_memory.read_instruction(address_of_instruction)
        state.program_counter += instruction.length
        pc_plus_instruction_length = address_of_instruction + instruction.length

        return InstructionFetchPipelineRegister(
            instruction=instruction,
            address_of_instruction=address_of_instruction,
            branch_prediction=False,
            pc_plus_instruction_length=pc_plus_instruction_length,
        )


class InstructionDecodeStage(Stage):
    def __init__(self, stages_until_writeback=2, detect_data_hazards=True) -> None:
        self.stages_until_writeback = stages_until_writeback
        self.detect_data_hazards = detect_data_hazards
        super().__init__()

    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """behavior of the ID Stage
        Should the pipeline_register not be InstructionFetchPipelineRegister it returns an
        InstructionDecodePipelineRegister with default values

        Args:
            pipeline_register (PipelineRegister): gets the InstructionFetchPipelineRegister as argument
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns InstructionDecodePipelineRegister with all information from
            the ID stage and all results of computations done in this step, as well as all controll signals
        """
        pipeline_register = pipeline_registers[index_of_own_input_register]

        if not isinstance(pipeline_register, InstructionFetchPipelineRegister):
            return InstructionDecodePipelineRegister()

        # uses the access_register_file method of the instruction saved in the InstructionFetchPipelineRegister
        # to get the data from the register files
        (
            register_read_addr_1,
            register_read_addr_2,
            register_read_data_1,
            register_read_data_2,
            imm,
        ) = pipeline_register.instruction.access_register_file(
            architectural_state=state
        )
        # gets the write register, used in the WB stage to find the register to write data to
        write_register = pipeline_register.instruction.get_write_register()

        # Data Hazard Detection
        flush_signal = None
        if self.detect_data_hazards:
            # Put all the write registers of later stages, that are not done ahead of this stage into a list
            write_registers_of_later_stages = [
                pipeline_registers[
                    index_of_own_input_register + i + 1
                ].instruction.get_write_register()
                for i in range(self.stages_until_writeback)
            ]
            # Check if there is a data hazard
            for register in write_registers_of_later_stages:
                if register is None or register == 0:
                    continue
                if register_read_addr_1 == register or register_read_addr_2 == register:
                    assert pipeline_register.address_of_instruction is not None
                    flush_signal = FlushSignal(
                        inclusive=True,
                        address=pipeline_register.address_of_instruction,
                    )
                    break

        # gets the control unit signals that are generated in the ID stage
        control_unit_signals = pipeline_register.instruction.control_unit_signals()
        return InstructionDecodePipelineRegister(
            instruction=pipeline_register.instruction,
            register_read_addr_1=register_read_addr_1,
            register_read_addr_2=register_read_addr_2,
            register_read_data_1=register_read_data_1,
            register_read_data_2=register_read_data_2,
            imm=imm,
            write_register=write_register,
            control_unit_signals=control_unit_signals,
            branch_prediction=pipeline_register.branch_prediction,
            flush_signal=flush_signal,
            pc_plus_instruction_length=pipeline_register.pc_plus_instruction_length,
            address_of_instruction=pipeline_register.address_of_instruction,
        )


class ExecuteStage(Stage):
    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """behavior of the EX stage
        Should the pipeline_register not be InstructionDecodePipelineRegister it returns an
        ExecutePipelineRegister with default values

        Args:
            pipeline_register (PipelineRegister): gets InstructionDecodePipelineRegister as argument
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns the ExecutePipelineRegister with all necessary information produced or
            used in the EX stage, as well as all controll signals
        """
        pipeline_register = pipeline_registers[index_of_own_input_register]

        if not isinstance(pipeline_register, InstructionDecodePipelineRegister):
            return ExecutePipelineRegister()

        alu_in_1 = (
            pipeline_register.register_read_data_1
            if pipeline_register.control_unit_signals.alu_src_1
            else pipeline_register.address_of_instruction
        )
        alu_in_2 = (
            pipeline_register.imm
            if pipeline_register.control_unit_signals.alu_src_2
            else pipeline_register.register_read_data_2
        )
        branch_taken, result = pipeline_register.instruction.alu_compute(
            alu_in_1=alu_in_1, alu_in_2=alu_in_2
        )
        pc_plus_imm = (
            pipeline_register.imm + pipeline_register.address_of_instruction
            if pipeline_register.imm is not None
            and pipeline_register.address_of_instruction is not None
            else None
        )

        return ExecutePipelineRegister(
            instruction=pipeline_register.instruction,
            alu_in_1=alu_in_1,
            alu_in_2=alu_in_2,
            register_read_data_1=pipeline_register.register_read_data_1,
            register_read_data_2=pipeline_register.register_read_data_2,
            imm=pipeline_register.imm,
            result=result,
            comparison=branch_taken,
            write_register=pipeline_register.write_register,
            control_unit_signals=pipeline_register.control_unit_signals,
            pc_plus_imm=pc_plus_imm,
            branch_prediction=pipeline_register.branch_prediction,
            pc_plus_instruction_length=pipeline_register.pc_plus_instruction_length,
            address_of_instruction=pipeline_register.address_of_instruction,
        )


class MemoryAccessStage(Stage):
    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """behavior of MEM stage
        Should the pipeline_register not be ExecutePipelineRegister it returns an MemoryAccessPipelineRegister
        with default values

        Args:
            pipeline_register (PipelineRegister): gets ExecutePipelineRegister as argument
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns MemoryAccessPipelineRegister with all necessary information produced or
            used in the MEM stage, as well as all controll signals
        """
        pipeline_register = pipeline_registers[index_of_own_input_register]

        if not isinstance(pipeline_register, ExecutePipelineRegister):
            return MemoryAccessPipelineRegister()

        memory_address = pipeline_register.result
        memory_write_data = pipeline_register.register_read_data_2
        memory_read_data = pipeline_register.instruction.memory_access(
            memory_address=memory_address,
            memory_write_data=memory_write_data,
            architectural_state=state,
        )
        comparison_or_jump = (
            pipeline_register.control_unit_signals.jump or pipeline_register.comparison
        )

        # NOTE: comparison_or_jump = 0 -> select (pc+i_length), comparison_or_jump = 1 -> select (pc+imm)
        incorrect_branch_prediction = (
            pipeline_register.control_unit_signals.branch
            and comparison_or_jump != pipeline_register.branch_prediction
        )

        if incorrect_branch_prediction or pipeline_register.control_unit_signals.jump:
            # flush if (pc+imm) should have been written to the pc
            assert pipeline_register.pc_plus_imm is not None
            flush_signal = FlushSignal(
                inclusive=False, address=pipeline_register.pc_plus_imm
            )
        elif pipeline_register.control_unit_signals.alu_to_pc:
            # flush if result should have been written to pc
            assert pipeline_register.result is not None
            flush_signal = FlushSignal(
                inclusive=False, address=pipeline_register.result
            )
        else:
            flush_signal = None

        if flush_signal is not None:
            if isinstance(pipeline_register.instruction, BTypeInstruction):
                state.performance_metrics.branch_count += 1
            elif isinstance(pipeline_register.instruction, JAL):
                state.performance_metrics.procedure_count += 1

        return MemoryAccessPipelineRegister(
            instruction=pipeline_register.instruction,
            memory_address=memory_address,
            result=pipeline_register.result,
            memory_write_data=memory_write_data,
            memory_read_data=memory_read_data,
            comparison=pipeline_register.comparison,
            comparison_or_jump=comparison_or_jump,
            write_register=pipeline_register.write_register,
            control_unit_signals=pipeline_register.control_unit_signals,
            pc_plus_imm=pipeline_register.pc_plus_imm,
            flush_signal=flush_signal,
            pc_plus_instruction_length=pipeline_register.pc_plus_instruction_length,
            imm=pipeline_register.imm,
            address_of_instruction=pipeline_register.address_of_instruction,
        )


class RegisterWritebackStage(Stage):
    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """behavior of WB stage
        Should the pipeline_register not be MemoryAccessPipelineRegister it returns an
        RegisterWritebackPipelineRegister with default values

        Args:
            pipeline_register (PipelineRegister): gets MemoryAccessPipelineRegister as argument
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns RegisterWritebackPipelineRegister with all necessary information produced or
            used in the WB stage, as well as all controll signals.
            Note: this information is not taken as an input by any other stage, because the WB stage is
            the last stage!
        """
        pipeline_register = pipeline_registers[index_of_own_input_register]

        if not isinstance(pipeline_register, MemoryAccessPipelineRegister):
            return RegisterWritebackPipelineRegister()

        if not isinstance(pipeline_register.instruction, EmptyInstruction):
            state.performance_metrics.instruction_count += 1

        # select the correct data for write back
        wb_src = pipeline_register.control_unit_signals.wb_src
        if wb_src == 0:
            register_write_data = pipeline_register.pc_plus_instruction_length
        elif wb_src == 1:
            register_write_data = pipeline_register.memory_read_data
        elif wb_src == 2:
            register_write_data = pipeline_register.result
        elif wb_src == 3:
            register_write_data = pipeline_register.imm
        else:
            register_write_data = None

        pipeline_register.instruction.write_back(
            write_register=pipeline_register.write_register,
            register_write_data=register_write_data,
            architectural_state=state,
        )

        return RegisterWritebackPipelineRegister(
            instruction=pipeline_register.instruction,
            register_write_data=register_write_data,
            write_register=pipeline_register.write_register,
            memory_read_data=pipeline_register.memory_read_data,
            alu_result=pipeline_register.result,
            control_unit_signals=pipeline_register.control_unit_signals,
            pc_plus_instruction_length=pipeline_register.pc_plus_instruction_length,
            imm=pipeline_register.imm,
            address_of_instruction=pipeline_register.address_of_instruction,
        )


#
# Single stage Pipeline:
#
class SingleStage(Stage):
    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """behavior of the single stage pipeline

        Args:
            pipeline_register (PipelineRegister): gets any PipelineRegister as argument, but does not use it
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns an PipelineRegister with default values
        """
        if state.instruction_at_pc():
            pc_before_increment = state.program_counter
            instr = state.instruction_memory.read_instruction(state.program_counter)

            state.performance_metrics.instruction_count += 1
            try:
                instr.behavior(state)
                state.program_counter += instr.length
                return PipelineRegister(
                    address_of_instruction=pc_before_increment,
                )
            except Exception as e:
                raise InstructionExecutionException(
                    address=pc_before_increment,
                    instruction_repr=instr.__repr__(),
                    error_message=e.__repr__(),
                )
        return PipelineRegister()


@dataclass
class FlushSignal:
    """A signal that all previous pipeline registers should be flushed and that the program counter should be set back"""

    # whether the pipeline register that holds this signal should be flushed too or not
    inclusive: bool
    # address to return to
    address: int
