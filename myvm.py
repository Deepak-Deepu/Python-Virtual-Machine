from sys import argv

LOAD_CONSTANT = 0x64
LOAD_NAME = 0x65
STORE_NAME = 0x5a
PRINT_ITEM = 0x47
PRINT_NEWLINE = 0x48
COMPARE_OP = 0x6b
BINARY_ADD = 0x17
BINARY_MULTIPLY = 0x14
BINARY_SUBTRACT = 0x18
POP_JUMP_IF_FALSE = 0x72
POP_BLOCK = 0x57
MAKE_FUNCTION = 0x84
RETURN_VALUE = 0x53
CALL_FUNCTION = 0x83
LOAD_FAST = 0x7c
STORE_FAST = 0x7d
LOAD_GLOBAL = 0x74

TYPE_TUPLE = 0x28
TYPE_INTEGER = 0x69
TYPE_STRING = 0x73
TYPE_CODE = 0x63
TYPE_NONE = 0x4e
TYPE_INTERN = 0x74
TYPE_SREF = 0x52
FUNCTION_START = 0x43

HAVE_ARG = 90

class Stack(object):
    def __init__(self):
        self.stack = []

    def push(self, data):
        self.stack.append(data)

    def pop(self):
        try:
            return self.stack.pop(-1)
        except IndexError:
            print 'Stack is empty'

    def get_top_n(self, num):
        try:
            return self.stack[-1 - num]
        except IndexError:
            print "there is only {} elements!".format(len(self.stack))

    def print_stack(self):
        print self.stack

stk = Stack()

def binaryadd(current):
    tos = stk.pop()
    tos1 = stk.pop()
    stk.push(tos1 + tos)
    return current + 1


def binarymul(current):
    tos = stk.pop()
    tos1 = stk.pop()
    stk.push(tos1 * tos)
    return current + 1


def binarysub(current):
    tos = stk.pop()
    tos1 = stk.pop()
    stk.push(tos1 - tos)
    return current + 1


def printitem(current):
    print stk.get_top_n(0),
    return current + 1


def printnewline(current):
    print
    return current + 1


def loadname(objcode, current):
    oparg = objcode.getoparg(current)
    name = objcode.names[oparg]
    if type(name) == int:
        stk.push(name)
    else:
        stk.push(objcode.names[oparg][0])
    return current + 3


def loadconst(objcode, current):
    oparg = objcode.getoparg(current)
    stk.push(objcode.consts[oparg])
    return current + 3


def loadglobal(objcode, current):
    oparg = objcode.getoparg(current)
    stk.push(objcode.names[oparg][0])
    return current + 3


def loadfast(objcode, current):
    oparg = objcode.getoparg(current)
    stk.push(objcode.varnames[oparg])
    return current + 3


def storename(objcode, current):
    oparg = objcode.getoparg(current)
    objcode.names[oparg] = stk.pop()
    return current + 3


def storefast(objcode, current):
    oparg = objcode.getoparg(current)
    objcode.varnames[oparg] = stk.pop()
    return current + 3


def popblock(current):
    return current + 1


def popjumpiffalse(objcode, current):
    if not stk.pop():
        return objcode.getoparg(current)
    else:
        return current + 3


def makefunction(objcode, current):
    return current + 9


def lessthan(op1, op2):
    return op1 < op2


def lessequal(op1, op2):
    return op1 <= op2


def equal(op1, op2):
    return op1 == op2



comparisons = {
    0: lessthan,
    1: lessequal,
    2: equal
}


def compareop(objcode, current):
    top = stk.pop()
    top1 = stk.pop()
    oparg = objcode.getoparg(current)
    stk.push(comparisons[oparg](top1, top))
    return current + 3



operations = {
    BINARY_ADD: binaryadd,
    BINARY_SUBTRACT: binarysub,
    BINARY_MULTIPLY: binarymul,
    LOAD_NAME: loadname,
    LOAD_FAST: loadfast,
    LOAD_CONSTANT: loadconst,
    LOAD_GLOBAL: loadglobal,
    STORE_NAME: storename,
    STORE_FAST: storefast,
    PRINT_ITEM: printitem,
    PRINT_NEWLINE: printnewline,
    POP_JUMP_IF_FALSE: popjumpiffalse,
    COMPARE_OP: compareop,
    MAKE_FUNCTION: makefunction
}


names = {}
name_count = 0


class Code(object):

    def __init__(self, pyclist, current=0):
        self.pyclist = pyclist
        self.current = current
        self.code = self.fun_code()
        self.consts = self.fun_consts()
        self.names = self.fun_names()
        self.varnames = self.fun_varnames()
        self.name = self.fun_name()

    def getname(self):
        return self.name

    def getcurrent(self):
        return self.current

    def getpyclist(self):
        return self.pyclist

    def getopcode(self, current):
        return self.code[current]

    def getoparg(self, current):
        return decimal(self.code, current)

    def Isend(self, current):
        if current >= len(self.code):
            return True
        else:
            return False

    def fun_code(self):
        pyclist = self.pyclist
        current = startofcode(pyclist, self.current)
        end = current + decimal(pyclist, current-5, 4)
        code = []
        while current < end:
            if not is_func_def(current, pyclist):
                if havearg(pyclist[current]):
                    code.extend(pyclist[current:current+3])
                    current += 3
                else:
                    code.append(pyclist[current])
                    current += 1
            else:
                code.append(MAKE_FUNCTION)
                code.extend([0] * 8)
                current += 9

        self.current = current
        return code

    def fun_consts(self):
        current = self.current
        pyclist = self.pyclist
        num_co = decimal(pyclist, current, 4)
        current += 5
        consts = []
        for dummy in range(num_co):
            if pyclist[current] == TYPE_INTEGER:
                consts.append(decimal(pyclist, current, 4))
                current += 5
            elif pyclist[current] == TYPE_NONE:
                consts.append(0)
                current += 1
            elif pyclist[current] == TYPE_CODE:
                objcode = Code(pyclist, current)
                f_index = objcode.getname()
                consts.append(objcode)
                names[f_index][0] = objcode
                current = end_of_code(pyclist, current)

        self.current = current
        return consts

    def fun_names(self):
        global name_count
        current = self.current
        pyclist = self.pyclist
        n_names = decimal(pyclist, current)
        func_index = 0
        current += 5
        co_names = {}
        index = 0
        for dummy in range(n_names):
            if (pyclist[current] == TYPE_INTERN):
                names[name_count] = [0]
                co_names[index] = names[name_count]
                name_count += 1
                index += 1
                current = skip_element(pyclist, current)
            elif (pyclist[current] == TYPE_SREF):
                func_index = decimal(pyclist, current)
                co_names[index] = names[func_index]
                index += 1
                current += 5
            else:
                current += 1

        self.current = current
        return co_names

    def fun_varnames(self):
        global name_count
        current = self.current
        pyclist = self.pyclist
        varnames = []
        n_varnames = decimal(pyclist, current, 4)
        current += 5
        for dummy in range(n_varnames):
            varnames.append(0)
            if pyclist[current] == TYPE_INTERN:
                names[name_count] = [0]
                name_count += 1
                current = skip_element(pyclist,  current)
            elif pyclist[current] == TYPE_SREF:
                current += 5
            else:
                current += 1

        self.current = current
        return varnames

    def fun_name(self):
        global name_count
        current = self.current
        pyclist = self.pyclist
        n_field = 0
        while True:
                if pyclist[current] == TYPE_TUPLE:
                    n_field += 1
                if n_field == 2:
                    break
                current += 1

        current += 5
        current = skip_element(pyclist, current)
        self.current = current
        if pyclist[current] == TYPE_INTERN:
            names[name_count] = [0]
            name_count += 1
            return name_count - 1

        else:
            return decimal(pyclist, current, 4)

    def view(self):
        print showpyc(self.code)
        print len(self.consts), 'constants'
        for index in range(len(self.consts)):
            if type(self.consts[index]) == int:
                print self.consts[index]
            else:
                self.consts[index].view()
        print self.names
        print self.varnames
        print self.name
        print 'global names'
        print names


limit = 2 ** 20


def readbytes(filename):
    with open(filename, "rb") as file_h:
        while True:
            chunk = file_h.read()
            if chunk:
                for byte in chunk:
                    yield ord(byte)
            else:
                break


def getpyclist(filename):
    lst = list(readbytes(filename))
    return lst


def showpyc(lst):
    return [hex(num) for num in lst]


def decimal(pyc_list, current, num_byte=2):
    value = 0
    factor = 0
    for index in range(num_byte):
        value |= pyc_list[current+index+1] << factor
        factor += 8
    if value >= limit:
        value = value - 2 * limit
    return value


def startofcode(pyc_list, current=0):
    while (pyc_list[current] != TYPE_CODE and
            pyc_list[current+17] != TYPE_STRING):
        current += 1
    if current == len(pyc_list) - 1:
        raise Exception("no code segment in the rest of the pyc")
    return current + 22


def skip_element(pycbuf, current):
    leng = decimal(pycbuf, current, 4)
    return current + leng + 5


def end_of_code(pyc_list, current=0):
    current += 17  

    current = skip_element(pyc_list, current)  
    n_const = decimal(pyc_list, current, 4)
    current += 5
    for dummy in range(n_const):
        if pyc_list[current] == TYPE_INTEGER:
            current += 5
        elif pyc_list[current] == TYPE_NONE:
            current += 1
        elif pyc_list[current] == TYPE_CODE:
            current = end_of_code(pyc_list, current)
        else:
            current += 1

    n_const = 0
    while True:
            if pyc_list[current] == TYPE_TUPLE:
                n_const += 1
            if n_const == 4:
                break
            current += 1

    current += 5
    current = skip_element(pyc_list, current)
    current = skip_element(pyc_list, current)

    current += 4
    current = skip_element(pyc_list, current)
    return current


def havearg(opcode):
    if opcode < HAVE_ARG:
        return False
    else:
        return True


def is_func_def(current, pycbuf):
    if pycbuf[current] == LOAD_CONSTANT and pycbuf[current+3] == MAKE_FUNCTION:
        return True
    else:
        return False


def get_op_arg(pycbuf, current):
    oparg = decimal(pycbuf, current)
    return oparg

def call_function(objcode, current):
    argc = objcode.getoparg(current)
    func = stk.get_top_n(argc)

    bkup_locals = func.varnames[:]

    while argc:
        argc -= 1
        func.varnames[argc] = stk.pop()

    stk.pop()
    execute(func)
    func.varnames = bkup_locals[:]
    return current + 3


def execute(objcode):
    current = 0
    while not objcode.Isend(current):
        opcode = objcode.getopcode(current)
        if opcode == CALL_FUNCTION:
            current = call_function(objcode, current)
            continue

        if opcode == RETURN_VALUE:
            return
        try:
            if havearg(opcode):
                current = operations[opcode](objcode, current)
            else:
                current = operations[opcode](current)

        except KeyError:
            msg = 'opcode {1} at {0} not found'.format(current, hex(opcode))
            raise Exception(msg)


def execute_pyc(pyc_file):
    pyc_lst = getpyclist(pyc_file)
    objcode = Code(pyc_lst)

    print
    execute(objcode)
    print


def main():
        pyc_file = argv[1]
        execute_pyc(pyc_file)

if __name__ == '__main__':
    main()
