#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "header.h"
#include "op_code.h"

void pop_top()
{
    pop();
}

void unary_not()
{
    int top = pop();
    push(!top);
}

void load_const(struct code_obj* pobj, int cur)
{
    int oparg = 0;
    oparg = get_element(&(pobj->code), cur+1);
    push(get_element(&(pobj->consts), oparg));
}

void load_name(struct code_obj* pobj, int cur)
{
    int oparg = get_element(&(pobj->code), cur+1);
    struct obj* name = pobj->names[oparg];
    if (name->type == TYPE_INTEGER)
        push(name->val.intval);
    else
        push(name->val.pobj);
}


void load_fast(struct code_obj* pobj, int cur)
{
    int oparg = get_element(&(pobj->code), cur+1);
    push(get_element(&(pobj->varnames), oparg));
}

void load_global(struct code_obj* pobj, int cur)
{
    int oparg = get_element(&(pobj->code), cur+1);
    struct obj* name = pobj->names[oparg];
    if (name->type == TYPE_INTEGER) {
        push((int)name->val.intval);
    } else {
        push(name->val.pobj);
    }
}

void store_name(struct code_obj* pobj, int cur)
{
    int oparg = get_element(&(pobj->code), cur+1);
    struct obj* name = pobj->names[oparg];
    if (name->type == TYPE_INTEGER)
        name->val.intval = pop();
    else
        name->val.pobj = (struct code_obj*) pop();
}

void store_fast(struct code_obj* pobj, int cur)
{
    int oparg = get_element(&(pobj->code), cur+1);
    set_element(&(pobj->varnames), oparg, pop());
}


int pop_jump_if_false(struct code_obj* pobj, int cur)
{
    if(!pop())
        return get_element(&(pobj->code), cur+1);
    else
        return cur+2;
}

int pop_jump_if_true(struct code_obj* pobj, int cur)
{
    if(pop())
        return get_element(&(pobj->code), cur+1);
    else
        return cur+2;
}

int jump_forward(struct code_obj* pobj, int cur)
{
    return cur + get_element(&(pobj->code), cur+1);
}

int jump_absolute(struct code_obj* pobj, int cur)
{
    return get_element(&(pobj->code), cur+1);
}

void compare_op(struct code_obj* pobj, int cur)
{
    int oparg = 0;
    int b = pop();
    int a = pop();
    int res = a == b;
    oparg = get_element(&(pobj->code), cur+1);
    switch(oparg) {
        case 0:
            res = a < b;
            break;
        case 1:
            res = res || a < b;
            break;
        case 2:
            break;
        case 3:
            res = !res;
            break;
        case 4:
            res = a > b;
            break;
        case 5:
            res = res || a > b;
            break;
        default:
            break;
    }
    push(res);
}

void print_item(void)
{
    int data = get_top_n(0);
    printf("%d", data);
}

void print_newline(void)
{
    printf("\n");
}

void binary_add(void)
{
    int first = pop();
    int second = pop();
    push(second + first);
}

void binary_multiply(void)
{
    push(pop() * pop());
}

void binary_divide(void)
{
    int first = pop();
    int sec = pop();
    push(sec / first);
}

void binary_modulo(void)
{
    int first = pop();
    int sec = pop();
    push(sec % first);
}

void binary_subtract(void)
{
    int first = pop();
    int sec = pop();
    push(sec - first);
}


struct code_obj* call_function(struct code_obj* pobj, int cur)
{
    int argc = get_element(&(pobj->code), cur+1);
    struct code_obj* pfun = (struct code_obj*) get_top_n(argc);
    int arg = 0;
    
    int length =  pfun->varnames.length;
    int* locals = malloc(sizeof (int) * length);
    

    while(length--) 
        locals[length] = get_element(&pfun->varnames, length);
    
   
    while(argc--) {
        arg = pop();
        set_element(&(pfun->varnames), argc, arg);
    }

    pop();
    
    execute(pfun);
    
 
    length = pfun->varnames.length;
    while(length--)
        set_element(&pfun->varnames, length, locals[length]);
}

