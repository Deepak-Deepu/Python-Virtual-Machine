#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "op_code.h"

#define MAXSTACK 500
static int stack[MAXSTACK] = {0};
static top = 0;
void print_stack()
{
    int i = 0;
    for(; i < top; i++)
        printf("%d | ", stack[i]);
    printf("\n");
}

void push(int data)
{
    if (top < MAXSTACK)
        stack[top++] = data;
    else
        printf("error: stack full, can't push %d\n", data);
}


void print_stack();
int pop(void)
{
    if (top > 0)
        return stack[--top];
    else {
        print_stack();
        printf("error: stack empty\n");
        getchar();
        return 0;
    }
}

int get_top_n(int n)
{
    return stack[top - n - 1];
}
