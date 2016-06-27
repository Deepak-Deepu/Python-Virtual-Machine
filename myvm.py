from sys import argv


LOAD_CONSTANT = 0x64
LOAD_NAME = 0x65
STORE_NAME = 0x5a
PRINT_ITEM = 0x47
PRINT_NEWLINE = 0x48
COMPARE_OP = 0x6b
BINARY_ADD = 0x17
BINARY_MULTIPLY = 0x14
BINARY_DIVIDE = 0x15
BINARY_SUBTRACT = 0x18
BINARY_MODULO = 0x16
POP_JUMP_IF_FALSE = 0x72
POP_JUMP_IF_TRUE = 0x73
JUMP_FORWARD = 0x6e
JUMP_ABSOLUTE = 0x71
SETUP_LOOP = 0x78
POP_BLOCK = 0x57
MAKE_FUNCTION = 0x84
RETURN_VALUE = 0x53
UNARY_NOT = 0xc
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


def pop_top(current):
    stk.pop()
    return current+1


def unary_not(current):
    stk.push(not stk.pop())
    return current + 1


def binary_add(current):
    tos = stk.pop()
    tos1 = stk.pop()
    stk.push(tos1 + tos)
    return current + 1


def binary_mul(current):
    tos = stk.pop()
    tos1 = stk.pop()
    stk.push(tos1 * tos)
    return current + 1


def binary_sub(current):
    tos = stk.pop()
    tos1 = stk.pop()
    stk.push(tos1 - tos)
    return current + 1


def binary_div(current):
    tos = stk.pop()
    tos1 = stk.pop()
    stk.push(tos1 / tos)
    return current + 1


def binary_modulo(current):
    tos = stk.pop()
    tos1 = stk.pop()
    stk.push(tos1 % tos)
    return current + 1


def print_item(current):
    print stk.get_top_n(0),
    return current + 1


def print_newline(current):
    print
    return current + 1


def load_name(objcode, current):
    oparg = objcode.get_oparg(current)
    name = objcode.names[oparg]
    if type(name) == int:
        stk.push(name)
    else:
        stk.push(objcode.names[oparg][0])
    return current + 3


def load_const(objcode, current):
    oparg = objcode.get_oparg(current)
    stk.push(objcode.consts[oparg])
    return current + 3


def load_global(objcode, current):
    oparg = objcode.get_oparg(current)
    stk.push(objcode.names[oparg][0])
    return current + 3


def load_fast(objcode, current):
    oparg = objcode.get_oparg(current)
    stk.push(objcode.varnames[oparg])
    return current + 3


def store_name(objcode, current):
    oparg = objcode.get_oparg(current)
    objcode.names[oparg] = stk.pop()
    return current + 3


def store_fast(objcode, current):
    oparg = objcode.get_oparg(current)
    objcode.varnames[oparg] = stk.pop()
    return current + 3


def setup_loop(objcode, current):
    return current + 3


def pop_block(current):
    return current + 1


def pop_jump_if_false(objcode, current):
    if not stk.pop():
        return objcode.get_oparg(current)
    else:
        return current + 3


def pop_jump_if_true(objcode, current):
    if stk.pop():
        return objcode.get_oparg(current)
    else:
        return current + 3


def jump_forward(objcode, current):
    return current + 3 + objcode.get_oparg(current)


def jump_absolute(objcode, current):
    return objcode.get_oparg(current)


def make_function(objcode, current):
    return current + 9


def less_than(op1, op2):
    return op1 < op2


def less_equal(op1, op2):
    return op1 <= op2


def equal(op1, op2):
    return op1 == op2


def not_equal(op1, op2):
    return op1 != op2


def greater_than(op1, op2):
    return op1 > op2


def grt_equal(op1, op2):
    return op1 >= op2


comparisons = {
    0: less_than,
    1: less_equal,
    2: equal,
    3: not_equal,
    4: greater_than,
    5: grt_equal
}


def compare_op(objcode, current):
    top = stk.pop()
    top1 = stk.pop()
    oparg = objcode.get_oparg(current)
    stk.push(comparisons[oparg](top1, top))
    return current + 3

operations = {
    BINARY_ADD: binary_add,
    BINARY_SUBTRACT: binary_sub,
    BINARY_MULTIPLY: binary_mul,
    BINARY_DIVIDE: binary_div,
    BINARY_MODULO: binary_modulo,
    LOAD_NAME: load_name,
    LOAD_FAST: load_fast,
    LOAD_CONSTANT: load_const,
    LOAD_GLOBAL: load_global,
    STORE_NAME: store_name,
    STORE_FAST: store_fast,
    PRINT_ITEM: print_item,
    PRINT_NEWLINE: print_newline,
    POP_JUMP_IF_FALSE: pop_jump_if_false,
    POP_JUMP_IF_TRUE: pop_jump_if_true,
    JUMP_FORWARD: jump_forward,
    JUMP_ABSOLUTE: jump_absolute,
    COMPARE_OP: compare_op,
    UNARY_NOT: unary_not,
    POP_TOP: pop_top,
    MAKE_FUNCTION: make_function,
    SETUP_LOOP: setup_loop,
    POP_BLOCK: pop_block
} 


names = {}
name_cnt = 0


class Code(object):

    def __init__(self, pyclist, current=0):
        self.pyclist = pyclist
        self.current = current
        self.code = self.fun_code()
        self.consts = self.fun_consts()
        self.names = self.fun_names()
        self.varnames = self.fun_names()
        self.name = self.acq_name()

    def get_name(self):
        return self.name

    def get_current(self):
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

    def fun_code(self):
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
                f_idx = objcode.get_name()
                consts.append(objcode)
                names[f_idx][0] = objcode
                current = end_of_code(pyclist, current)

        self.current = current
        return consts

    def fun_names(self):
        global name_cnt
        current = self.current
        pyclist = self.pyclist
        n_names = decimal(pyclist, current)
        func_idx = 0
        current += 5
        co_names = {}
        idx = 0
        for dummy in range(n_names):
            # first occurrentrence of a name
            if (pyclist[current] == TYPE_INTERN):
                names[name_cnt] = [0]
                co_names[idx] = names[name_cnt]
                name_cnt += 1
                idx += 1
                current = skip_element(pyclist, current)
            elif (pyclist[current] == TYPE_SREF):
                func_idx = decimal(pyclist, current)
                co_names[idx] = names[func_idx]
                idx += 1
                current += 5
            else:
                current += 1

        self.current = current
        return co_names

    def fun_names(self):
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
            elif pyclist[current] == TYPE_SREF:
                current += 5
            else:
                current += 1

        self.current = current
        return varnames

    def acq_name(self):
        global name_cnt
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
            names[name_cnt] = [0]
            name_cnt += 1
            return name_cnt - 1

        else:
            return decimal(pyclist, current, 4)

    def view(self):
        print "****************"
        print show_pyc(self.code)
        print len(self.consts), 'constants'
        for idx in range(len(self.consts)):
            if type(self.consts[idx]) == int:
                print self.consts[idx]
            else:
                self.consts[idx].view()
        print self.names
        print self.varnames
        print self.name
        print 'global names'
        print names
        print '--------------------------------'

INT_LIMIT = 2 ** 20


def read_bytes(filename):
    with open(filename, "rb") as file_h:
        while True:
            chunk = file_h.read()
            if chunk:
                for byte in chunk:
                    yield ord(byte)
            else:
                break


def get_pyc_list(filename):
    lst = list(read_bytes(filename))
    return lst


def show_pyc(lst):
    return [hex(num) for num in lst]


def decimal(pyc_list, current, num_byte=2):
    value = 0
    factor = 0
    for idx in range(num_byte):
        value |= pyc_list[current+idx+1] << factor
        factor += 8
    if value >= INT_LIMIT:
        value = value - 2 * INT_LIMIT
    return value


def start_of_code(pyc_list, current=0):
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


def call_function(objcode, current):

    argc = objcode.get_oparg(current)
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
    
    pyc_lst = get_pyc_list(pyc_file)

    objcode = Code(pyc_lst)

    print
    execute(objcode)
    print


def main():

        pyc_file = argv[1]
        execute_pyc(pyc_file)

if __name__ == '__main__':
    main()
