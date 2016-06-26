from stack import Stack
from sys import argv
from code import Code

stkoff = Stack()

LOAD_CONSTANT = 0x64
LOAD_NAME = 0x65
PRINT_ITEM = 0x47
PRINT_NEWLINE = 0x48
BINARY_ADD = 0x17
MAKE_FUNCTION = 0x84
RETURN_VALUE = 0x53
CALL_FUNCTION = 0x83
LOAD_FAST = 0x7c
STORE_FAST = 0x7d
LOAD_GLOBAL = 0x74
POP_TOP = 0x1


TYPE_TUPLE = 0x28
TYPE_INTEGER = 0x69
TYPE_STRING = 0x73
TYPE_CODE = 0x63
TYPE_NONE = 0x4e
TYPE_INTERN = 0x74
TYPE_SREF = 0x52
FUNCTION_START = 0x43

HAVE_ARG = 90

def printitem(current):
    print stkoff.get_top_n(0),
    return current + 1


def loadconst(codeobj, current):
    oparg = codeobj.get_oparg(current)
    stkoff.push(codeobj.consts[oparg])
    return current + 3
   
def storefast(objcode, current):
    oparg = objcode.get_oparg(current)
    objcode.varnames[oparg] = stkoff.pop()
    return current + 3

def loadfast(objcode, current):
    oparg = objcode.get_oparg(current)
    stkoff.push(objcode.varnames[oparg])
    return current + 3        

def binaryadd(current):
	tos= stkoff.pop()
	tos1 = stkoff.pop()
	stkoff.push(tos1 + tos)
	return current + 1 

def makefunction(objcode, current):
	return current + 9

def loadname(objcode, current):
    oparg = objcode.get_oparg(current)
    name = objcode.names[oparg]
    if type(name) == int:
        stkoff.push(name)
    else:
        stkoff.push(objcode.names[oparg][0])
    return current + 3

def printnewline(current):
    print
    return current + 1



operations = {
    BINARY_ADD: binaryadd,
    LOAD_NAME: loadname,
    LOAD_FAST: loadfast,
    LOAD_CONSTANT: loadconst,
    STORE_FAST: storefast,
    PRINT_ITEM: printitem,
    PRINT_NEWLINE: printnewline,
    MAKE_FUNCTION: makefunction
}

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



INT_LIMIT = 2 ** 31

def read_bytes(filename):
    with open(filename, "rb") as file_h:
        while True:
            chunk = file_h.read()
            if chunk:
                for byte in chunk:
                    yield ord(byte)
            else:
                break


def get_pycfile(filename):
    lst = list(read_bytes(filename))
    return lst


def show_pyc(lst):
    return [hex(num) for num in lst]


def decimal(pycfile, current, num_byte=2):
    value = 0
    factor = 0
    for index in range(num_byte):
        value |= pycfile[current+index+1] << factor
        factor += 8
    if value >= INT_LIMIT:
        value = value - 2 * INT_LIMIT
    return value


def start_of_code(pycfile, current=0):
    while (pycfile[current] != TYPE_CODE and
            pycfile[current+17] != TYPE_STRING):
        current += 1
    if current == len(pycfile) - 1:
        raise Exception("no code segment in the rest of the pyc")
    return current + 22


def skip_element(pycbuf, current):
    leng = decimal(pycbuf, current, 4)
    return current + leng + 5


def end_of_code(pycfile, current=0):

    current += 17  # now cur is at byte code s:73 , start of the code string

    current = skip_element(pycfile, current)  # skipping the code string

    # skipping the co_consts field
    n_const = decimal(pycfile, current, 4)
    current += 5
    for dummy in range(n_const):
        if pycfile[current] == TYPE_INTEGER:
            current += 5
        elif pycfile[current] == TYPE_NONE:
            current += 1
        elif pycfile[current] == TYPE_CODE:
            current = end_of_code(pycfile, current)
        else:
            current += 1

    # skip 4 (:28 s that is co_names, varnames, cellvars, freevars
    n_const = 0
    while True:
            if pycfile[current] == TYPE_TUPLE:
                n_const += 1
            if n_const == 4:
                break
            current += 1

    current += 5
    # skip filenmae
    current = skip_element(pycfile, current)

    # skip function name
    current = skip_element(pycfile, current)

    # skip first line number
    current += 4

    # skip lnotab
    current = skip_element(pycfile, current)
    return current


def have_arg(opcode):
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


# named objects of the form name : object
names = {}
name_cnt = 0

class Code(object):
    

    def __init__(self, pyclist, current=0):
        
        self.pyclist = pyclist
        self.current = current
        self.code = self.code()
        self.consts = self.consts()
        self.names = self.names()
        self.varnames = self.varnames()
        self.name = self.name()

    def get_name(self):
        return self.name

    def get_cur(self):
        return self.current

    def get_pyclist(self):
        return self.pyclist

    def get_opcode(self, current):
        return self.code[current]

    def get_oparg(self, current):
        return decimal(self.code, current)

    def is_end(self, current):
        if current >= len(self.code):
            return True
        else:
            return False

    def code(self):
        pyclist = self.pyclist
        current = start_of_code(pyclist, self.current)
        end = current + decimal(pyclist, current-5, 4)
        code = []
        while current < end:
            if not is_func_def(current, pyclist):
                if have_arg(pyclist[current]):
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

    def consts(self):
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
                f_index = objcode.get_name()
                consts.append(objcode)
                names[f_index][0] = objcode
                current = end_of_code(pyclist, current)

        self.current = current
        return consts

    def names(self):
        global name_cnt
        current = self.current
        pyclist = self.pyclist
        n_names = decimal(pyclist, current)
        func_index = 0
        current += 5
        co_names = {}
        index = 0
        for dummy in range(n_names):
            if (pyclist[current] == TYPE_INTERN):
                names[name_cnt] = [0]
                co_names[index] = names[name_cnt]
                name_cnt += 1
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

    def varnames(self):
        global name_cnt
        current = self.current
        pyclist = self.pyclist
        varnames = []
        n_varnames = decimal(pyclist, current, 4)
        current += 5
        for dummy in range(n_varnames):
            varnames.append(0)
            if pyclist[current] == TYPE_INTERN:
                names[name_cnt] = [0]
                name_cnt += 1
                current = skip_element(pyclist,  current)
            elif pyclist[cur] == TYPE_SREF:
                current += 5
            else:
                current += 1

        self.current = current
        return varnames

    def name(self):
        global name_cnt
        current = self.current
        pyclist = self.pyclist
        n_field = 0
        # skip 2 (:28 s that is cellvars and freevars
        while True:
                if pyclist[current] == TYPE_TUPLE:
                    n_field += 1
                if n_field == 2:
                    break
                current += 1

        current += 5
        # skip filenmae
        current = skip_element(pyclist, current)
        self.current = current
        # getting the index of the name  of the code
        if pyclist[current] == TYPE_INTERN:
            names[name_cnt] = [0]
            name_cnt += 1
            return name_cnt - 1

        else:
            return decimal(pyclist, current, 4)

    def view(self):
        print "****************"
        print show_pyc(self.code)
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
        print '--------------------------------'


def call_function(objcode, current):
    argc = objcode.get_oparg(current)
    func = stkoff.get_top_n(argc)

    # backup func's local vars
    bkup_locals = func.varnames[:]

    while argc:
        argc -= 1
        func.varnames[argc] = stkoff.pop()

    stkoff.pop()
    execute(func)

    # restore func's local vars
    func.varnames = bkup_locals[:]

    return current + 3


def execute(objcode):
    current = 0
    while not objcode.is_end(current):
        opcode = objcode.get_opcode(current)

        if opcode == CALL_FUNCTION:
            current = call_function(objcode, current)
            continue

        if opcode == RETURN_VALUE:
            return

        try:
            if have_arg(opcode):
                current = operations[opcode](objcode, current)
            else:
                current = operations[opcode](current)

        except KeyError:
            msg = 'opcode {1} at {0} not found'.format(current, hex(opcode))
            raise Exception(msg)


def execute_pyc(pyc_file):
    # getting the bytecode as a list of bytes
    pyc_lst = get_pycfile(pyc_file)

    # getting the codeobject from the pyc list
    objcode = Code(pyc_lst)

    # executing the code object
    print
    execute(objcode)
    print


def main():
    if len(argv) != 2 or '.pyc' not in argv[1]:
        print 'usage: pyvm.py filename.pyc'

    else:
        pyc_file = argv[1]
        execute_pyc(pyc_file)

if __name__ == '__main__':
    main()
