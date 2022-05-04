# Project: Interpreter for IPP 2022
# Author:  Marko Kubrachenko
# Date:    29.03.2022

import re
import argparse
import sys
import xml.etree.ElementTree as ET

# Global variables
source_file = None
input_file = None
input_data = []

instruction_list = []
labels = {}
GF = {}
LF_stack = []
TF = None
stack = []
call_stack = []

label_pos = 0
current_instr = 0

# Nil class
class Nil:
    def __init__(self):
        self.value = "nil"

# Frame class
class Frame:
    def __init__(self):
        self._vars = {}

    def get_vars(self):
        return self._vars

    def get_var(self, id):
        return self._vars[id]

    def set_var(self, id, value):
        self._vars[id] = value

# Instruction class
class Instruction:
    def __init__(self, opcode, order):
        self.set_opcode(opcode)
        self.set_order(order)
        self.append_instr()
        self._args = []

    def get_opcode(self):
        return self._opcode
    def set_opcode(self, opcode):
        self._opcode = opcode

    def get_order(self):
        return self._order
    def set_order(self, order):
        self._order = order

    def get_list(self):
        return instruction_list
    def append_instr(self):
        instruction_list.append(self)

    def get_arg(self, num):
        return self._args[num]
    def append_arg(self, type, value):
        if type == "string":
            unicodes = re.findall(r'(\\[0-9]{3})+', str(value))
            for unicode in unicodes:
                char = chr(int(unicode[1:]))
                value = value.replace(unicode, char)

        self._args.append(Argument(type, value))

# Argument class
class Argument:
    def __init__(self, type: str, value):
        self.set_type(type)
        self.set_value(value)

    def get_value(self):
        return self._value
    def set_value(self, value):
        self._value = value

    def get_type(self):
        return self._type
    def set_type(self, type):
        self._type = type

# Factory class
class Factory:
    @classmethod
    def resolve(cls, opcode: str, num):
        if opcode.upper() == "MOVE":
            return MOVE(num)
        elif opcode.upper() == "CREATEFRAME":
            return CREATEFRAME(num)
        elif opcode.upper() == "PUSHFRAME":
            return PUSHFRAME(num)
        elif opcode.upper() == "POPFRAME":
            return POPFRAME(num)
        elif opcode.upper() == "DEFVAR":
            return DEFVAR(num)
        elif opcode.upper() == "CALL":
            return CALL(num)
        elif opcode.upper() == "RETURN":
            return RETURN(num)
        elif opcode.upper() == "PUSHS":
            return PUSHS(num)
        elif opcode.upper() == "POPS":
            return POPS(num)
        elif opcode.upper() == "ADD":
            return ADD(num)
        elif opcode.upper() == "SUB":
            return SUB(num)
        elif opcode.upper() == "MUL":
            return MUL(num)
        elif opcode.upper() == "IDIV":
            return IDIV(num)
        elif opcode.upper() == "LT":
            return LT(num)
        elif opcode.upper() == "GT":
            return GT(num)
        elif opcode.upper() == "EQ":
            return EQ(num)
        elif opcode.upper() == "AND":
            return AND(num)
        elif opcode.upper() == "OR":
            return OR(num)
        elif opcode.upper() == "NOT":
            return NOT(num)
        elif opcode.upper() == "INT2CHAR":
            return INT2CHAR(num)
        elif opcode.upper() == "STRI2INT":
            return STRI2INT(num)
        elif opcode.upper() == "READ":
            return READ(num)
        elif opcode.upper() == "WRITE":
            return WRITE(num)
        elif opcode.upper() == "CONCAT":
            return CONCAT(num)
        elif opcode.upper() == "STRLEN":
            return STRLEN(num)
        elif opcode.upper() == "GETCHAR":
            return GETCHAR(num)
        elif opcode.upper() == "SETCHAR":
            return SETCHAR(num)
        elif opcode.upper() == "TYPE":
            return TYPE(num)
        elif opcode.upper() == "LABEL":
            return LABEL(num)
        elif opcode.upper() == "JUMP":
            return JUMP(num)
        elif opcode.upper() == "JUMPIFEQ":
            return JUMPIFEQ(num)
        elif opcode.upper() == "JUMPIFNEQ":
            return JUMPIFNEQ(num)
        elif opcode.upper() == "EXIT":
            return EXIT(num)
        elif opcode.upper() == "DPRINT":
            return DPRINT(num)
        elif opcode.upper() == "BREAK":
            return BREAK(num)
        else:
            print("unknown instruction: " + opcode, file=sys.stderr)
            exit(32)

# DEFVAR class
class DEFVAR(Instruction):
    def __init__(self, number):
        super().__init__("DEFVAR", number)

    def check_args(self):
        if self.get_arg(0).get_type() != "var":
            exit(53)

    def execute(self):
        self.check_args()
        frame = self.get_arg(0).get_value().split("@", 1)[0]
        key = self.get_arg(0).get_value().split("@", 1)[1]

        if frame == "GF":
            if not key in GF:
                GF[key] = None
            else:
                print(key + " already exists in GF", file=sys.stderr)
                exit(52)
        elif frame == "LF":
            if len(LF_stack) != 0:
                LF = LF_stack[-1]
                if not key in LF.get_vars():
                    LF.get_vars()[key] = None
                else:
                    print(key + " already exists in LF", file=sys.stderr)
                    exit(52)
            else:
                print("cannot declare "+ key + ", because LF doesn't exist", file=sys.stderr)
                exit(55)
        elif frame == "TF":
            if TF != None:
                if not key in TF.get_vars():
                    TF.set_var(key, None)
                else:
                    print(key + " already exists in TF", file=sys.stderr)
                    exit(52)
            else:
                print("cannot declare "+ key + ", because TF doesn't exist", file=sys.stderr)
                exit(55)

# MOVE class
class MOVE(Instruction):
    def __init__(self, number):
        super().__init__("MOVE", number)

    def execute(self):
        data = None
        arg1 = self.get_arg(1)
        if arg1.get_type() == "var":
            src_frame = arg1.get_value().split("@", 1)[0]
            src_key = arg1.get_value().split("@", 1)[1]
            data = get_var(src_frame, src_key)

        elif arg1.get_type() == "string":
            if arg1.get_value() == None:
                data = ""
            else:
                data = str(arg1.get_value())

        elif arg1.get_type() == "int" and bool(re.match(r"^[+-]?[\d]+$", arg1.get_value())):
            data = int(arg1.get_value())
        elif arg1.get_type() == "bool" and bool(re.match(r"^true|false$", arg1.get_value())):
            data = to_bool(arg1.get_value())
        elif arg1.get_type() == "nil" and bool(re.match(r"^nil$", arg1.get_value())):
            data = Nil()
        else:
            print("bad types of operands in MOVE instruction", file=sys.stderr)
            exit(53)

        dst_frame = self.get_arg(0).get_value().split("@", 1)[0]
        dst_key = self.get_arg(0).get_value().split("@", 1)[1]
        store_var(dst_frame, dst_key, data)

# LABEL class
class LABEL(Instruction):
    def __init__(self, number):
        super().__init__("LABEL", number)

    def label_append(self):
        if not self.get_arg(0).get_value() in labels:
            labels[self.get_arg(0).get_value()] = label_pos
        else:
            print("this label already exists", file=sys.stderr)
            exit(52)

    def execute(self):
        return

# JUMP class
class JUMP(Instruction):
    def __init__(self, number):
        super().__init__("JUMP", number)

    def execute(self):
        global current_instr
        dst = self.get_arg(0).get_value()
        if dst in labels:
            current_instr = labels.get(dst)
        else:
            print("this label does not exist", file=sys.stderr)
            exit(52)

# CREATEFRAME class
class CREATEFRAME(Instruction):
    def __init__(self, number):
        super().__init__("CREATEFRAME", number)

    def execute(self):
        global TF
        TF = Frame()

# PUSHFRAME class
class PUSHFRAME(Instruction):
    def __init__(self, number):
        super().__init__("PUSHFRAME", number)

    def execute(self):
        # dont forget to make set TF back to None
        global TF
        if TF != None:
            LF_stack.append(TF)
            TF = None
        else:
            print("there is no frame to push", file=sys.stderr)
            exit(55)

# POPFRAME class
class POPFRAME(Instruction):
    def __init__(self, number):
        super().__init__("POPFRAME", number)

    def execute(self):
        global TF
        if len(LF_stack) != 0:
            TF = LF_stack.pop()
        else:
            print("there is no TF on the stack", file=sys.stderr)
            exit(55)

# ADD class
class ADD(Instruction):
    def __init__(self, number):
        super().__init__("ADD", number)

    def execute(self):
        value1 = get_int(self.get_arg(1))
        value2 = get_int(self.get_arg(2))
        if isinstance(value1, Nil) or isinstance(value2, Nil):
            result = Nil
        else:
            result = value1 + value2
        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], result)

# SUB class
class SUB(Instruction):
    def __init__(self, number):
        super().__init__("SUB", number)

    def execute(self):
        value1 = get_int(self.get_arg(1))
        value2 = get_int(self.get_arg(2))
        if isinstance(value1, Nil) or isinstance(value2, Nil):
            result = Nil
        else:
            result = value1 - value2
        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], result)

# MUL class
class MUL(Instruction):
    def __init__(self, number):
        super().__init__("MUL", number)

    def execute(self):
        value1 = get_int(self.get_arg(1))
        value2 = get_int(self.get_arg(2))
        if isinstance(value1, Nil) or isinstance(value2, Nil):
            result = Nil
        else:
            result = value1 * value2
        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], result)

# IDIV Class
class IDIV(Instruction):
    def __init__(self, number):
        super().__init__("IDIV", number)

    def execute(self):
        value1 = get_int(self.get_arg(1))
        value2 = get_int(self.get_arg(2))
        result = None
        if isinstance(value1, Nil) or isinstance(value2, Nil):
            result = Nil
        else:
            try:
                result = get_int(self.get_arg(1)) // get_int(self.get_arg(2))
            except:
                print("division by zero", file=sys.stderr)
                exit(57)
        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], result)

# AND class
class AND(Instruction):
    def __init__(self, number):
        super().__init__("AND", number)

    def execute(self):
        value1 = get_bool(self.get_arg(1))
        value2 = get_bool(self.get_arg(2))
        result = value1 and value2
        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], result)

# OR class
class OR(Instruction):
    def __init__(self, number):
        super().__init__("OR", number)

    def execute(self):
        value1 = get_bool(self.get_arg(1))
        value2 = get_bool(self.get_arg(2))
        result = value1 or value2
        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], result)

# NOT class
class NOT(Instruction):
    def __init__(self, number):
        super().__init__("NOT", number)

    def execute(self):
        value = get_bool(self.get_arg(1))
        result = not value
        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], result)

# WRITE class
class WRITE(Instruction):
    def __init__(self, number):
        super().__init__("WRITE", number)

    def execute(self):
        data = None
        if self.get_arg(0).get_type() == "var":
            frame = self.get_arg(0).get_value().split("@", 1)[0]
            key = self.get_arg(0).get_value().split("@", 1)[1]
            data = get_var(frame, key)
            if (data == None):
                data = ""
            elif (data in (True, False)):
                data = str(data).lower()
            elif (isinstance(data, Nil) or data == Nil):
                data = ""
            # string and int straight print

        elif self.get_arg(0).get_type() == "nil":
            data = ""
        elif self.get_arg(0).get_type() == "bool":
            data = self.get_arg(0).get_value().lower()
        elif self.get_arg(0).get_type() == "string":
            data = self.get_arg(0).get_value()
        elif self.get_arg(0).get_type() == "int":
            data = self.get_arg(0).get_value()
        else:
            # never bad operand according to the task
            print("bad operand type WRITE " + self.get_order(), file=sys.stderr)
            exit(53)

        print(data, end = "")

# INT2CHAR class
class INT2CHAR(Instruction):
    def __init__(self, number):
        super().__init__("INT2CHAR", number)

    def execute(self):
        data = None
        if self.get_arg(1).get_type() == "var":
            frame = self.get_arg(1).get_value().split("@", 1)[0]
            key = self.get_arg(1).get_value().split("@", 1)[1]
            data = get_var(frame, key)
            if (not type(data) == int):
                print("value is not int", file=sys.stderr)
                exit(53)

        elif self.get_arg(1).get_type() == "int" and bool(re.match(r"^[+-]?[\d]+$", self.get_arg(1).get_value())):
            data = int(self.get_arg(1).get_value())
        else:
            print("bad type of operand", file=sys.stderr)
            exit(53)

        try:
            data = chr(data)
        except:
            exit(58)

        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], data)

# CONCAT class
class CONCAT(Instruction):
    def __init__(self, number):
        super().__init__("CONCAT", number)

    def execute(self):
        if self.get_arg(0).get_type() == "var":
            frame = self.get_arg(0).get_value().split("@", 1)[0]
            key = self.get_arg(0).get_value().split("@", 1)[1]
            value1 = None
            value2 = None
            result = None
            if self.get_arg(1).get_type() == "string" and self.get_arg(2).get_type() == "string":
                value1 = self.get_arg(1).get_value()
                if value1 == None:
                    value1 = ""
                value2 = self.get_arg(2).get_value()
                if value2 == None:
                    value2 = ""
            elif self.get_arg(1).get_type() == "var" and self.get_arg(2).get_type() == "var":
                frame1 = self.get_arg(1).get_value().split("@", 1)[0]
                key1 = self.get_arg(1).get_value().split("@", 1)[1]
                value1 = get_var(frame1, key1)
                frame2 = self.get_arg(2).get_value().split("@", 1)[0]
                key2 = self.get_arg(2).get_value().split("@", 1)[1]
                value2 = get_var(frame2, key2)
            elif self.get_arg(1).get_type() == "var" and self.get_arg(2).get_type() == "string":
                frame1 = self.get_arg(1).get_value().split("@", 1)[0]
                key1 = self.get_arg(1).get_value().split("@", 1)[1]
                value1 = get_var(frame1, key1)
                value2 = self.get_arg(2).get_value()
                if value2 == None:
                    value2 = ""
            elif self.get_arg(1).get_type() == "string" and self.get_arg(2).get_type() == "var":
                value1 = self.get_arg(1).get_value()
                if value1 == None:
                    value1 = ""
                frame2 = self.get_arg(2).get_value().split("@", 1)[0]
                key2 = self.get_arg(2).get_value().split("@", 1)[1]
                value2 = get_var(frame2, key2)
            else:
                print("operands must be same type in CONCAT", file=sys.stderr)
                exit(53)

            try:
                result = value1 + value2
            except:
                print("error 53: operand must be same type in CONCAT", file=sys.stderr)
                exit(53)
            finally:
                store_var(frame, key, result)

# LT class
class LT(Instruction):
    def __init__(self, number):
        super().__init__("LT", number)

    def execute(self):
        value1 = get_any(self.get_arg(1))
        value2 = get_any(self.get_arg(2))

        if (isinstance(value1, Nil) or value1 == Nil) or (isinstance(value2, Nil) or value2 == Nil):
            print("error 53: nil type in LT", file=sys.stderr)
            exit(53)
        result = None
        if type(value1) == type(value2):
            result = value1 < value2
        else:
            print("error 53: operands in LT instruction must be the same type", file=sys.stderr)
            exit(53)
        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], result)

# GT class
class GT(Instruction):
    def __init__(self, number):
        super().__init__("GT", number)

    def execute(self):
        value1 = get_any(self.get_arg(1))
        value2 = get_any(self.get_arg(2))

        if (isinstance(value1, Nil) or value1 == Nil) or (isinstance(value2, Nil) or value2 == Nil):
            print("error 53: nil type in GT", file=sys.stderr)
            exit(53)
        result = None
        if type(value1) == type(value2):
            result = value1 > value2
        else:
            print("error 53: operands in GT instruction must be the same type", file=sys.stderr)
            exit(53)
        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], result)

# EQ class
class EQ(Instruction):
    def __init__(self, number):
        super().__init__("EQ", number)

    def execute(self):
        value1 = get_any(self.get_arg(1))
        value2 = get_any(self.get_arg(2))
        result = None

        if (isinstance(value1, Nil) or value1 == Nil) and (isinstance(value2, Nil) or value2 == Nil):
            result = True
        else:
            if (isinstance(value1, Nil) or value1 == Nil) or (isinstance(value2, Nil) or value2 == Nil):
                result = False
            else:
                if type(value1) == type(value2):
                    result = value1 == value2
                else:
                    print("error 53: operands in EQ instruction must be the same type", file=sys.stderr)
                    exit(53)
        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], result)

# PUSHS class
class PUSHS(Instruction):
    def __init__(self, number):
        super().__init__("PUSHS", number)

    def execute(self):
        value = get_any(self.get_arg(0))
        stack.append(value)

# POPS class
class POPS(Instruction):
    def __init__(self, number):
        super().__init__("POPS", number)

    def execute(self):
        frame = self.get_arg(0).get_value().split("@", 1)[0]
        key = self.get_arg(0).get_value().split("@", 1)[1]
        if len(stack) != 0:
            value = stack.pop()
            store_var(frame, key, value)
        else:
            print("the stack is empty", file=sys.stderr)
            exit(56)

# JUMPIFEQ class
class JUMPIFEQ(Instruction):
    def __init__(self, number):
        super().__init__("EQ", number)

    def execute(self):
        global current_instr
        value1 = get_any(self.get_arg(1))
        value2 = get_any(self.get_arg(2))
        result = None

        dst = self.get_arg(0).get_value()
        if not dst in labels:
            print("label \"" + dst + "\" does not exist", file=sys.stderr)
            exit(52)

        if (isinstance(value1, Nil) or value1 == Nil) and (isinstance(value2, Nil) or value2 == Nil):
            result = True
        else:
            if type(value1) == type(value2):
                result = value1 == value2
            else:
                print("error 53: operands in JUMPIFEQ instruction must be the same type", file=sys.stderr)
                exit(53)

        if result == True:
                current_instr = labels.get(dst)

# JUMPIFNEQ class
class JUMPIFNEQ(Instruction):
    def __init__(self, number):
        super().__init__("EQ", number)

    def execute(self):
        global current_instr
        value1 = get_any(self.get_arg(1))
        value2 = get_any(self.get_arg(2))
        result = None

        dst = self.get_arg(0).get_value()
        if not dst in labels:
            print("label \"" + dst + "\" does not exist", file=sys.stderr)
            exit(52)

        if (isinstance(value1, Nil) or value1 == Nil) and (isinstance(value2, Nil) or value2 == Nil):
            result = False
        else:
            if type(value1) == type(value2):
                result = value1 != value2
            else:
                print("error 53: operands in JUMPIFNEQ instruction must be the same type", file=sys.stderr)
                exit(53)

        if result == True:
                current_instr = labels.get(dst)

# EXIT class
class EXIT(Instruction):
    def __init__(self, number):
        super().__init__("EXIT", number)

    def execute(self):
        value = get_int(self.get_arg(0))
        if value < 0 or value > 49:
            print("exit code must between 0 and 49 (included)", file=sys.stderr)
            exit(57)
        else:
            exit(value)

# CALL class
class CALL(Instruction):
    def __init__(self, number):
        super().__init__("CALL", number)

    def execute(self):
        global current_instr
        dst = self.get_arg(0).get_value()
        if dst in labels:
            call_stack.append(current_instr)
            current_instr = labels.get(dst)
        else:
            print("this label does not exist", file=sys.stderr)
            exit(52)

# RETURN class
class RETURN(Instruction):
    def __init__(self, number):
        super().__init__("RETURN", number)

    def execute(self):
        global current_instr
        if len(call_stack) != 0:
            current_instr = call_stack.pop()
        else:
            print("the call-stack is empty", file=sys.stderr)
            exit(56)

# READ class
class READ(Instruction):
    def __init__(self, number):
        super().__init__("READ", number)

    def execute(self):
        type = self.get_arg(1).get_value()
        data = None
        if input_data == []:
            try:
                data = input()
            except:
                data = Nil()

        else:
            if len(input_data) > 0:
                data = input_data.pop(0)

        if type == "bool":
            if data.upper() == "TRUE":
                data = True
            else:
                data = False
        elif type == "int" and bool(re.match(r"^[+-]?[\d]+$", data)):
            data = int(data)
        elif type == "string":
            data = str(data)
        else:
            data = Nil()

        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], data)

# TYPE class
class TYPE(Instruction):
    def __init__(self, number):
        super().__init__("TYPE", number)

    def execute(self):
        data = get_any(self.get_arg(1))

        if data == None:
            data = ""
        elif isinstance(data, Nil):
            data = "nil"
        elif type(data) == int:
            data = "int"
        elif type(data) == bool:
            data = "bool"
        elif isinstance(data, str):
            data = "string"
        else:
            print("bad argument type in TYPE", file=sys.stderr)
            exit(53)
        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], data)

# DPRINT class
class DPRINT(Instruction):
    def __init__(self, number):
        super().__init__("DPRINT", number)

    def execute(self):
        data = None
        if self.get_arg(0).get_type() == "var":
            frame = self.get_arg(0).get_value().split("@", 1)[0]
            key = self.get_arg(0).get_value().split("@", 1)[1]
            data = get_var(frame, key)
            if (data == None):
                data = ""
            elif (data in (True, False)):
                data = str(data).lower()
            elif (isinstance(data, Nil) or data == Nil):
                data = ""
            # string and int straight print

        elif self.get_arg(0).get_type() == "nil":
            data = ""
        elif self.get_arg(0).get_type() == "bool":
            data = self.get_arg(0).get_value().lower()
        elif self.get_arg(0).get_type() == "string":
            data = self.get_arg(0).get_value()

        elif self.get_arg(0).get_type() == "int":
            data = self.get_arg(0).get_value()
        else:
            # never bad operand according to the task
            print("bad operand type DPRINT " + self.get_order(), file=sys.stderr)
            exit(53)

        print(data, end = "", file=sys.stderr)

# BREAK class
class BREAK(Instruction):
    def __init__(self, number):
        super().__init__("BREAK", number)

    def execute(self):
        print("Current instruction is " + str(instruction_list[current_instr].get_opcode()) +
              " with order " + str(instruction_list[current_instr].get_order()), file=sys.stderr)
        print("GF is " + str(GF), file=sys.stderr)

# STRI2INT class
class STRI2INT(Instruction):
    def __init__(self, number):
        super().__init__("STRI2INT", number)

    def execute(self):
        data = None
        if self.get_arg(1).get_type() == "var":
            frame = self.get_arg(1).get_value().split("@", 1)[0]
            key = self.get_arg(1).get_value().split("@", 1)[1]
            data = get_var(frame, key)
            if (not isinstance(data, str)):
                print("bad operands in STRI2INT", file=sys.stderr)
                exit(53)
        elif self.get_arg(1).get_type() == "string":
            data = self.get_arg(1).get_value()
        else:
            print("bad operands in STRI2INT", file=sys.stderr)
            exit(53)

        position = get_int(self.get_arg(2))
        if position >= len(data) or position < 0:
            print("index in STRI2INT is out of range", file=sys.stderr)
            exit(58)

        try:
            result = ord(data[position])
        except:
            print("error in STRI2INT", file=sys.stderr)
            exit(58)

        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], result)

# STRLEN class
class STRLEN(Instruction):
    def __init__(self, number):
        super().__init__("STRLEN", number)

    def execute(self):
        data = None
        if self.get_arg(1).get_type() == "var":
            frame = self.get_arg(1).get_value().split("@", 1)[0]
            key = self.get_arg(1).get_value().split("@", 1)[1]
            data = get_var(frame, key)
            if (not isinstance(data, str)):
                print("bad operands in STRLEN", file=sys.stderr)
                exit(53)
        elif self.get_arg(1).get_type() == "string":
            data = self.get_arg(1).get_value()
        else:
            print("bad operands in STRLEN", file=sys.stderr)
            exit(53)

        if data == None:
            data = ""

        try:
            result = len(data)
        except:
            print("bad operands in STRLEN", file=sys.stderr)
            exit(53)
        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], result)

# GETCHAR class
class GETCHAR(Instruction):
    def __init__(self, number):
        super().__init__("GETCHAR", number)

    def execute(self):
        data = None
        if self.get_arg(1).get_type() == "var":
            frame = self.get_arg(1).get_value().split("@", 1)[0]
            key = self.get_arg(1).get_value().split("@", 1)[1]
            data = get_var(frame, key)
            if (not isinstance(data, str)):
                print("bad operands in GETCHAR", file=sys.stderr)
                exit(53)
        elif self.get_arg(1).get_type() == "string":
            data = self.get_arg(1).get_value()
        else:
            print("bad operands in GETCHAR", file=sys.stderr)
            exit(53)

        position = get_int(self.get_arg(2))
        if position >= len(data) or position < 0:
            print("index in GETCHAR is out of range", file=sys.stderr)
            exit(58)

        try:
            result = data[position]
        except:
            print("error in GETCHAR", file=sys.stderr)
            exit(58)

        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], result)

# SETCHAR class
class SETCHAR(Instruction):
    def __init__(self, number):
        super().__init__("SETCHAR", number)

    def execute(self):
        value = get_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1])
        if (not isinstance(value, str)):
            print("bad operands in SETCHAR", file=sys.stderr)
            exit(53)

        data = None
        if self.get_arg(2).get_type() == "var":
            frame = self.get_arg(2).get_value().split("@", 1)[0]
            key = self.get_arg(2).get_value().split("@", 1)[1]
            data = get_var(frame, key)
            if (not isinstance(data, str)):
                print("bad operands in SETCHAR", file=sys.stderr)
                exit(53)
        elif self.get_arg(2).get_type() == "string":
            data = self.get_arg(2).get_value()
        else:
            print("bad operands in SETCHAR", file=sys.stderr)
            exit(53)

        position = get_int(self.get_arg(1))
        if position >= len(value) or position < 0 or data == None:
            print("index in SETCHAR is out of range", file=sys.stderr)
            exit(58)

        try:
            value = value[:position] + data[0] + value[position + 1:]
        except:
            print("error in SETCHAR", file=sys.stderr)
            exit(58)

        store_var(self.get_arg(0).get_value().split("@", 1)[0], self.get_arg(0).get_value().split("@", 1)[1], value)


####### Functions used for interpreting #######
# function used for different instructions
def get_any(arg):
    if arg.get_type() == "var":
        src_frame = arg.get_value().split("@", 1)[0]
        src_key = arg.get_value().split("@", 1)[1]
        return get_var(src_frame, src_key)
    elif arg.get_type() == "string":
        if arg.get_value() == None:
            return ""
        else:
            return str(arg.get_value())
    elif arg.get_type() == "int" and bool(re.match(r"^[+-]?[\d]+$", arg.get_value())):
        return int(arg.get_value())
    elif arg.get_type() == "bool" and bool(re.match(r"^true|false$", arg.get_value())):
        return to_bool(arg.get_value())
    elif arg.get_type() == "nil" and bool(re.match(r"^nil$", arg.get_value())):
        return Nil()
    else:
        print("bad type of " + arg.get_value(), file=sys.stderr)
        exit(53)

# helpful function for true-false instructions
def to_bool(arg):
    if arg.upper() == "TRUE":
        return True
    elif arg.upper() == "FALSE":
        return False

# function used to get bool for logic operations
def get_bool(arg):
    if arg.get_type() == "var":
        frame = arg.get_value().split("@", 1)[0]
        key = arg.get_value().split("@", 1)[1]
        value = get_var(frame, key)
        if isinstance(value, bool):
            return value
        else:
            print("value is not bool", file=sys.stderr)
            exit(53)
    elif arg.get_type() == "bool" and bool(re.match(r"^true|false$", arg.get_value())):
        return to_bool(arg.get_value())
    else:
        print("bad type of operand", file=sys.stderr)
        exit(53)

# function used to get int for math operations
def get_int(arg):
    if arg.get_type() == "var":
        frame = arg.get_value().split("@", 1)[0]
        key = arg.get_value().split("@", 1)[1]
        value = get_var(frame, key)

        if type(value) == int:
            return value
        #elif isinstance(value, Nil) or value == Nil:
        #    return Nil()
        else:
            print(str(value) + " is not int", file=sys.stderr)
            exit(53)
    elif arg.get_type() == "int" and bool(re.match(r"^[+-]?[\d]+$", arg.get_value())):
        return int(arg.get_value())
    #elif arg.get_type() == "nil" and bool(re.match(r"^nil$", arg.get_value())):
    #    return Nil()
    else:
        print("bad type of operand", file=sys.stderr)
        exit(53)

# store the value depending on frame name
def store_var(frame, key, value):
    if frame == "GF":
        if key in GF:
            GF[key] = value
        else:
            print("var with name " + key + " doesn't exist in GF", file=sys.stderr)
            exit(54)

    elif frame == "LF":
        if len(LF_stack) != 0:
            LF = LF_stack[-1]
            if key in LF.get_vars():
                LF.get_vars()[key] = value
            else:
                print("var with name " + key + " doesn't exist in LF", file=sys.stderr)
                exit(54)
        else:
            print("cannot store " + key + ", because LF doesn't exist", file=sys.stderr)
            exit(55)

    elif frame == "TF":
        if TF != None:
            if key in TF.get_vars():
                TF.set_var(key, value)
            else:
                print("var with name " + key + " doesn't exist in TF", file=sys.stderr)
                exit(54)
        else:
            print("cannot store " + key + ", because TF doesn't exist", file=sys.stderr)
            exit(55)

# return the value stored in some frame
def get_var(frame, key):
        value = None
        if frame == "GF":
            if key in GF:
                value = GF[key]
            else:
                print("var with name " + key + " doesn't exist in GF", file=sys.stderr)
                exit(54)
        elif frame == "LF":
            if len(LF_stack) != 0:
                LF = LF_stack[-1]
                if key in LF.get_vars():
                    value = LF.get_vars()[key]
                else:
                    print("var with name " + key + " doesn't exist in LF", file=sys.stderr)
                    exit(54)
            else:
                print("cannot get " + key + ", because LF doesn't exist", file=sys.stderr)
                exit(55)

        elif frame == "TF":
            if TF != None:
                if key in TF.get_vars():
                    value = TF.get_var(key)
                else:
                    print("var with name " + key + " doesn't exist in TF", file=sys.stderr)
                    exit(54)
            else:
                print("cannot get " + key + ", because TF doesn't exist", file=sys.stderr)
                exit(55)
        # return the value
        if value == None:
            print("undefined varible", file=sys.stderr)
            exit(56)
        return value


###### Other functions ######
# function to parse arguments
def parse_args():
    # check for --help param
    if '--help' in sys.argv:
        if len(sys.argv) > 2:
            exit(10)
        else:
            print("HELP:\n"
                  "\t--help          print the help\n"
                  "\t--source=path   specify the source file\n"
                  "\t--input=path    specify the input file")
            exit(0)

    global source_file, input_file
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', nargs=1, type=str)
    parser.add_argument('--input', nargs=1, type=str)
    try:
        args = parser.parse_args()
    except:
        exit(10)

    if args.source and args.input:
        source_file, input_file = ''.join(args.source), ''.join(args.input)
    elif args.source:
        source_file = ''.join(args.source)
    elif args.input:
        input_file = ''.join(args.input)
    else:
        exit(10)

# function to read the input
def read_input():
    global input_data
    if input_file != None:
        try:
            with open(input_file, "r") as file_variable:
                for line in file_variable:
                    input_data.append(line.replace("\n", ""))
            file_variable.close()
        except:
            print("it was impossible to open the input-file", file=sys.stderr)
            exit(11)

# function to check if xml syntax is correct
def check_xml(source_file):
    try:
        xml_tree = ET.parse(source_file)
    except:
        print("bad formatted xml", file=sys.stderr)
        exit(31)
    xml_root = xml_tree.getroot()
    if xml_root.tag != "program":
        print("bad xml tag \"program\"", file=sys.stderr)
        exit(32)
    if 'language' not in list(xml_root.attrib.keys()):
        print("no attribute \"language\" in xml", file=sys.stderr)
        exit(32)

    xml_ords = []
    for xml_child in xml_root:
        if xml_child.tag != "instruction":
            print("bad xml tag \"instruction\"", file=sys.stderr)
            exit(32)
        # get order and opcode keys
        ord_opc = list(xml_child.attrib.keys())
        if 'order' not in ord_opc or 'opcode' not in ord_opc:
            print("bad attributes \"order\" or \"opcode\" in xml", file=sys.stderr)
            exit(32)
        xml_ords.append(xml_child.get("order"))

        xml_args = []
        for arg in xml_child:
            xml_args.append(arg.tag)
            if not (re.match('^arg[123]$', arg.tag)):
                print("bad arguments in xml", file=sys.stderr)
                exit(32)
        # check if there are no duplicate arg tags
        if not (len(set(xml_args)) == len(xml_args)):
            print("there are duplicated args", file=sys.stderr)
            exit(32)
    # check if there are no duplicated orders or negative ones
    if not (len(set(xml_ords)) == len(xml_ords)):
        print("there are duplicated orders of instructions", file=sys.stderr)
        exit(32)
    if not (all((ords).isdigit() == True for ords in xml_ords)):
        print("there are bad number in order of instructions", file=sys.stderr)
        exit(32)
    if not (all(int(ords) > 0 for ords in xml_ords)):
        print("there are negative orders of instructions", file=sys.stderr)
        exit(32)
    return xml_root

# function to sort the layers of xml file
def sort_xml(xml_root):
    # sort instructions by order
    xml_root[:] = sorted(xml_root, key=lambda child: (child.tag, int(child.get('order'))))
    # sort arguments
    for child in xml_root:
        child[:] = sorted(child, key=lambda child: (child.tag))
    return xml_root

# function to work out xml
def workout_xml(source_file):
    xml_root = check_xml(source_file)
    xml_root = sort_xml(xml_root)
    return xml_root

# transfer instructions to objects
def instr_to_object(xml_root):
    for instr in xml_root:
        i = Factory.resolve(instr.get("opcode"), instr.get("order"))
        for arg in instr:
            i.append_arg(arg.get("type"), arg.text)


##### Main function #####
def main():
    global label_pos
    global current_instr
    # work out users arguments
    parse_args()
    # read the input file or stdin
    read_input()
    # work out xml file
    xml_root = workout_xml(source_file)
    # transfer instruction's data to objects
    instr_to_object(xml_root)
    # set up the labels
    for instr in instruction_list:
        if instr.get_opcode().upper() == "LABEL":
            instr.label_append()
        label_pos += 1

    # execute
    while current_instr < len(instruction_list):
        instruction_list[current_instr].execute()
        current_instr += 1

# start
if __name__ == '__main__':
    main()