# Project: Interpreter for IPP 2022
# Author:  Marko Kubrachenko
# Date:    29.03.2022

# TODO
# store the fucking type of the value into frame too

import re
import argparse
import xml.etree.ElementTree as ET

instruction_list = []
labels = []
GF = {}
LF = []
TF = None
stack = []

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
            return
        elif opcode.upper() == "RETURN":
            return
        elif opcode.upper() == "PUSHS":
            return
        elif opcode.upper() == "POPS":
            return
        elif opcode.upper() == "ADD":
            return ADD(num)
        elif opcode.upper() == "SUB":
            return SUB(num)
        elif opcode.upper() == "MUL":
            return MUL(num)
        elif opcode.upper() == "IDIV":
            return IDIV(num)
        elif opcode.upper() == "LT":
            return
        elif opcode.upper() == "GT":
            return
        elif opcode.upper() == "EQ":
            return
        elif opcode.upper() == "AND":
            return AND(num)
        elif opcode.upper() == "OR":
            return OR(num)
        elif opcode.upper() == "NOT":
            return NOT(num)
        elif opcode.upper() == "INT2CHAR":
            return INT2CHAR(num)
        elif opcode.upper() == "STRI2INT":
            return
        elif opcode.upper() == "READ":
            return
        elif opcode.upper() == "WRITE":
            return WRITE(num)
        elif opcode.upper() == "CONCAT":
            return CONCAT(num)
        elif opcode.upper() == "STRLEN":
            return
        elif opcode.upper() == "GETCHAR":
            return
        elif opcode.upper() == "SETCHAR":
            return
        elif opcode.upper() == "TYPE":
            return
        elif opcode.upper() == "LABEL":
            return LABEL(num)
        elif opcode.upper() == "JUMP":
            return
        elif opcode.upper() == "JUMPIFEQ":
            return
        elif opcode.upper() == "JUMPIFNEQ":
            return
        elif opcode.upper() == "EXIT":
            return
        elif opcode.upper() == "DPRINT":
            return
        elif opcode.upper() == "BREAK":
            return
        else:
            exit(52)

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
                print(key + " already exists in GF")
                exit(52)
        elif frame == "LF":
            if len(LF) != 0:
                local_frame = LF[-1]
                if not key in local_frame.get_vars():
                    local_frame[key] = None
                else:
                    print(key + " already exists in LF")
                    exit(52)
            else:
                print("cannot declare "+ key + ", because LF doesn't exist")
                exit(55)
        elif frame == "TF":
            if TF != None:
                if not key in TF.get_vars():
                    TF.set_var(key, None)
                else:
                    print(key + " already exists in TF")
                    exit(52)
            else:
                print("cannot declare "+ key + ", because TF doesn't exist")
                exit(55)

# MOVE class
class MOVE(Instruction):
    def __init__(self, number):
        super().__init__("MOVE", number)

    def check_args(self):
        if self.get_arg(0).get_type() != "var":
            exit(53)
        if self.get_arg(1).get_type() not in ("string", "var", "int"):
            exit(53)

    def execute(self):
        self.check_args()
        data = None
        if self.get_arg(1).get_type() == "var":
            src_frame = self.get_arg(1).get_value().split("@", 1)[0]
            src_key = self.get_arg(1).get_value().split("@", 1)[1]
            data = get_var(src_frame, src_key)

        elif self.get_arg(1).get_type() == "string":
            if self.get_arg(1).get_value() == None:
                data = ""
            else:
                data = str(self.get_arg(1).get_value())
        elif self.get_arg(1).get_type() == "int":
            data = int(self.get_arg(1).get_value())

        dst_frame = self.get_arg(0).get_value().split("@", 1)[0]
        dst_key = self.get_arg(0).get_value().split("@", 1)[1]
        store_var(dst_frame, dst_key, data)

# LABEL class
class LABEL(Instruction):
    def __init__(self, number):
        super().__init__("LABEL", number)
        #self.label_append()

    def label_append(self):
        if not self.get_arg(0).get_value() in labels:
            labels.append(self)
        else:
            print("this label already exists")
            exit(52)

    def execute(self):
        return

# CREATEFRAME class
class CREATEFRAME(Instruction):
    def __init__(self, number):
        super().__init__("CREATEFRAME", number)
    # TODO consider what if TF already exists and next instruction is CREATEFRAME
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
            LF.append(TF)
            TF = None
        else:
            print("there is no frame to push")
            exit(55)

# POPFRAME class
class POPFRAME(Instruction):
    def __init__(self, number):
        super().__init__("POPFRAME", number)

    def execute(self):
        global TF
        # TODO check the condition
        if LF is not None:
            TF = LF.pop()
        else:
            print("there is no TF on the stack")
            exit(55)

# ADD class
class ADD(Instruction):
    def __init__(self, number):
        super().__init__("ADD", number)

    def check_args(self):
        if self.get_arg(1).get_type() != "int" or self.get_arg(2).get_type() != "int":
            exit(53)

    def execute(self):
        return int(self.get_arg(1).get_value()) + int(self.get_arg(2).get_value())

# SUB class
class SUB(Instruction):
    def __init__(self, number):
        super().__init__("SUB", number)

    def check_args(self):
        if self.get_arg(1).get_type() != "int" or self.get_arg(2).get_type() != "int":
            exit(53)

    def execute(self):
        return int(self.get_arg(1).get_value()) - int(self.get_arg(2).get_value())

# MUL class
class MUL(Instruction):
    def __init__(self, number):
        super().__init__("MUL", number)

    def check_args(self):
        if self.get_arg(1).get_type() != "int" or self.get_arg(2).get_type() != "int":
            exit(53)

    def execute(self):
        return int(self.get_arg(1).get_value()) * int(self.get_arg(2).get_value())

# IDIV Class
class IDIV(Instruction):
    def __init__(self, number):
        super().__init__("IDIV", number)

    def check_args(self):
        if self.get_arg(1).get_type() != "int" or self.get_arg(2).get_type() != "int":
            exit(53)
        if int(self.get_arg(2).get_value()) == 0:
            exit(57)

    def execute(self):
        return int(self.get_arg(1).get_value()) / int(self.get_arg(2).get_value())

# AND class
class AND(Instruction):
    def __init__(self, number):
        super().__init__("AND", number)

    def check_args(self):
        if self.get_arg(1).get_type() != "bool" or self.get_arg(2).get_type() != "bool":
            exit(53)

    def execute(self):
        self.check_args()
        return to_bool(self.get_arg(1).get_value()) and to_bool(self.get_arg(2).get_value())

# OR class
class OR(Instruction):
    def __init__(self, number):
        super().__init__("OR", number)

    def check_args(self):
        if self.get_arg(1).get_type() != "bool" or self.get_arg(2).get_type() != "bool":
            exit(53)

    def execute(self):
        self.check_args()
        return to_bool(self.get_arg(1).get_value()) or to_bool(self.get_arg(2).get_value())

# NOT class
class NOT(Instruction):
    def __init__(self, number):
        super().__init__("NOT", number)

    def check_args(self):
        if self.get_arg(1).get_type() != "bool":
            exit(53)

    def execute(self):
        self.check_args()
        return not to_bool(self.get_arg(1).get_value())

# WRITE class
class WRITE(Instruction):
    def __init__(self, number):
        super().__init__("WRITE", number)

    def execute(self):
        if self.get_arg(0).get_type() == "var":
            frame = self.get_arg(0).get_value().split("@", 1)[0]
            key = self.get_arg(0).get_value().split("@", 1)[1]
            data = get_var(frame, key)
            print(data if data != None else "", end = "")
        elif self.get_arg(0).get_type() == "nil":
            print("", end = "")
        elif self.get_arg(0).get_type() == "bool":
            print(self.get_arg(0).get_value().lower(), end = "")
        elif self.get_arg(0).get_type() == "string":
            print(self.get_arg(0).get_value(), end = "")
        else:
            exit(53)

# INT2CHAR class
class INT2CHAR(Instruction):
    def __init__(self, number):
        super().__init__("INT2CHAR", number)

    def check_args(self):
        if self.get_arg(0).get_type() != "var" or self.get_arg(1).get_type() != "int":
            exit(55)

    def execute(self):
        self.check_args()
        data = None
        if (self.get_arg(1).get_type() == "var"):
            frame2 = self.get_arg(1).get_value().split("@", 1)[0]
            key2 = self.get_arg(1).get_value().split("@", 1)[1]
            data = get_var(frame2, key2)

        try:
            data = chr(int(self.get_arg(1).get_value()))
        except:
            exit(58)

        frame1 = self.get_arg(0).get_value().split("@", 1)[0]
        key1 = self.get_arg(0).get_value().split("@", 1)[1]
        store_var(frame1, key1, data)

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
                value2 = self.get_arg(2).get_value()
            elif self.get_arg(1).get_type() == "var" and self.get_arg(2).get_type() == "var":
                frame1 = self.get_arg(1).get_value().split("@", 1)[0]
                key1 = self.get_arg(1).get_value().split("@", 1)[1]
                value1 = get_var(frame1, key1)
                frame2 = self.get_arg(2).get_value().split("@", 1)[0]
                key2 = self.get_arg(2).get_value().split("@", 1)[1]
                value2 = get_var(frame2, key2)
            else:
                exit(53)

            try:
                result = value1 + value2
            except:
                print("yep")
                exit(53)
            finally:
                store_var(frame, key, result)

####### Functions used for interpreting #######
# helpful function for true-false instructions
def to_bool(arg):
    if arg.upper() == "TRUE":
        return True
    elif arg.upper() == "FALSE":
        return False
    else:
        exit(55)

# store the value depending on frame name
def store_var(frame, key, value):
    if frame == "GF":
        if key in GF:
            GF[key] = value
        else:
            exit(54)

    elif frame == "LF":
        if len(LF) != 0:
            local_frame = LF[-1]
            if key in local_frame.get_vars():
                local_frame.get_vars()[key] = value
            else:
                exit(54)
        else:
            print("cannot store "+ key + ", because LF doesn't exist")
            exit(55)

    elif frame == "TF":
        if TF != None:
            if key in TF.get_vars():
                TF.set_var(key, value)
            else:
                exit(54)
        else:
            print("cannot store " + key + ", because TF doesn't exist")
            exit(55)

# return the value stored in some frame
def get_var(frame, key):
        value = None
        if frame == "GF":
            if key in GF:
                value = GF[key]
            else:
                exit(54)
        elif frame == "LF":
            if len(LF) != 0:
                local_frame = LF[-1]
                if key in local_frame.get_vars():
                    value = local_frame.get_vars()[key]
                else:
                    exit(54)
            else:
                print("cannot get " + key + ", because LF doesn't exist")
                exit(55)

        elif frame == "TF":
            if TF != None:
                if key in TF.get_vars():
                    value = TF.get_var(key)
                else:
                    exit(54)
            else:
                print("cannot get " + key + ", because TF doesn't exist")
                exit(55)
        # return the value
        return value

###### Other functions for the project ######
# function to parse arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', nargs=1, type=str)
    parser.add_argument('--input', nargs=1, type=str)
    try:
        args = parser.parse_args()
    except:
        exit(55)

    if args.source and args.input:
        return(''.join(args.source), ''.join(args.input))
    elif args.source:
        return(''.join(args.source), None)
    elif args.input:
        return(None, ''.join(args.input))
    else:
        exit(55)

# function to check if xml syntax is correct
def check_xml(source_file):
    xml_tree = ET.parse(source_file)
    xml_root = xml_tree.getroot()
    if xml_root.tag != "program":
        print("Error suka!")
    for xml_child in xml_root:
        if xml_child.tag != "instruction":
            print("Error suka!")
        # get order and opcode keys
        ord_opc = list(xml_child.attrib.keys())
        if 'order' not in ord_opc or 'opcode' not in ord_opc:
            print("Error suka!")

        for arg in xml_child:
            if not (re.match('^arg[123]$', arg.tag)):
                print("Error suka!")
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

# main function
def main():
    # work out users arguments
    source_file, input_file = parse_args()
    # work out xml file
    xml_root = workout_xml(source_file)
    # transfer instruction's data to objects
    instr_to_object(xml_root)
    # set up the labels
    for instr in instruction_list:
        if instr.get_opcode().upper() == "LABEL":
            instr.label_append()

    # do da ting
    for instr in instruction_list:
        instr.execute()

    #print(isinstance(LF.pop().get_vars().get('biba'), int))

    #print(re.sub(r'(\\)(\d\d\d)', , "AHOJ\032SVETE"))

    #example = "AHOJ\032SVETE"
    #result = example.index('\\')
    #result = example.replace(strcat("\", num), chr(num))
    #result = re.findall(r'(\\[0-9]{3})+', example)
    #for uni in result:
    #    ch = chr(int(uni[1:]))
    #    finish = finish.replace(uni, ch)
    #    print(finish)

    #xmlstr = ET.tostring(xml_root, encoding="utf-8", method="xml")
    #print(xmlstr.decode("utf-8"))

# Let the magic start!!
if __name__ == '__main__':
    main()