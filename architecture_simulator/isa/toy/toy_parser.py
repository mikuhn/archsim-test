import pyparsing as pp

from ..parser import ParserSyntaxException
from .toy_instructions import AddressTypeInstruction, ToyInstruction, instruction_map


class ToyParser:
    ADDRESS_MNEMONICS = ["STO", "LDA", "BRZ", "ADD", "SUB", "OR", "AND", "XOR"]
    NO_ADDRESS_MNEMONICS = ["NOT", "INC", "DEC", "ZRO", "NOP"]

    pattern_hex_address = pp.Combine("$" + pp.Word(pp.hexnums, exact=3))

    pattern_address_instruction = pp.oneOf(ADDRESS_MNEMONICS, caseless=True)(
        "mnemonic"
    ) + pattern_hex_address("address")

    pattern_no_address_instruction = pp.oneOf(NO_ADDRESS_MNEMONICS, caseless=True)(
        "mnemonic"
    )

    pattern_line = (
        pattern_address_instruction ^ pattern_no_address_instruction
    ) + pp.StringEnd().suppress()

    def parse(self, program: str) -> list[ToyInstruction]:
        """Parses a program into instruction objects.

        Args:
            program (str): A string containing (possibly multiple, newline separated) instrucions. May contain comments (#) and empty lines.

        Raises:
            ParserSyntaxException: A syntax error if the parser could not understand the program.

        Returns:
            list[ToyInstruction]: A list of instruction objects which were used in the program.
        """
        sanitized_program = self._sanitize(program)
        instructions = []
        for linenumber, line in sanitized_program:
            try:
                tokens = self.pattern_line.parse_string(line)
                instructions.append(self._tokens_to_instruction(tokens))
            except pp.ParseException:
                raise ParserSyntaxException(line_number=linenumber, line=line)
        return instructions

    def _sanitize(self, program: str) -> list[tuple[int, str]]:
        """Removes leading/trailing whitespaces, empty lines, comments. Gives each line a linenumber (starting at 1)

        Args:
            program (str): A string containing possibly multiple instructions (separated by newlines), comments, ...

        Returns:
            list[tuple[int, str]]: A list of (linenumber, instruction) where instruction does not contain any bloat.
        """
        lines = program.splitlines()
        sanitized_program: list[tuple[int, str]] = []
        for index, line in enumerate(lines):
            # remove leading/trailing whitespaces
            line = line.strip()
            # skip empty lines and lines that start with a # (comments)
            if (not line) or line.startswith("#"):
                continue
            # strip comments that start after (possible) instructions
            instruction_part = line.split("#", maxsplit=1)[0].strip()
            # append linenumber (index+1) and instruction string
            sanitized_program.append((index + 1, instruction_part))
        return sanitized_program

    def _tokens_to_instruction(self, tokens: pp.ParseResults) -> ToyInstruction:
        """Pyparsing returns parse results for each line. This function converts tokens from one line into one instruction object with matching arguments.

        Args:
            tokens (pp.ParseResults): The tokens from one instruction.

        Returns:
            ToyInstruction: A matching instruction object.
        """
        mnemonic = tokens.mnemonic.upper()
        instruction_class = instruction_map[mnemonic]
        if issubclass(instruction_class, AddressTypeInstruction):
            address = self._address_to_int(tokens.address)
            return instruction_class(address=address)
        return instruction_class()

    def _address_to_int(self, address: str) -> int:
        """Convert addresses to ints. Currently, only hex addresses, given in the '$abc' format are accepted.

        Args:
            address (str): An address like '$abc'

        Returns:
            int: the corresponding integer.
        """
        return int(address[1:], base=16)
