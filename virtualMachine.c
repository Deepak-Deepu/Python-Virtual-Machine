#include<stdio.h>
#include<stdlib.h>


#define PUSH(vm, v) vm->stack[++vm->sp] = v
#define POP(vm)     vm->stack[vm->sp--]
#define NCODE(vm)   vm->code[vm->pc++]

#define STACK_SIZE 100


	 char co_varnames[] = {'a','b'};
         char co_names[] = {};
         int co_consts[] = {0,10,20};


enum {
        LOAD_CONST = 1,
        STORE_FAST = 2,
        LOAD_FAST  = 3,
        BINARY_ADD = 4,
        RETURN_VALUE = 5
};



typedef struct {
	int* loacls; 
	int* code;   
	int* stack;  
	int pc;	     
	int sp;      
	int fp;	     
	}VM;

VM* newVM(int* code,	
 int pc,		
 int datasize)		
{

	VM* vm = (VM*)malloc(sizeof(VM));
	vm->code = code;
	vm->pc = pc;
	vm->sp = -1;
	vm->loacls = (int *)malloc(sizeof(int) * datasize);
	vm->stack = (int *)malloc(sizeof(int) * STACK_SIZE);
	
	return vm;
}

		
void delVM(VM* vm)
{
	free(vm->loacls);
	free(vm->stack);
	free(vm);
}


void run(VM* vm)
{

	
	do {
		if(NCODE(vm) >= 0) 
		{
		int opcode = NCODE(vm);
		int v=0, a=0,b=0;
//		printf(" %d",opcode);
		switch(opcode)
		{
		case LOAD_CONST:
			v=NCODE(vm);
//			printf(" %d \n",v);
			PUSH(vm, co_consts[v]);
//		        printf(" %d ",co_consts[v]);
			break;

		case STORE_FAST:
			v=NCODE(vm);
//			printf("%d \n",v);
			co_varnames[v]=POP(vm);
			break;

		case LOAD_FAST:
			v=NCODE(vm);
			PUSH(vm, co_varnames[v]);
			break;

		case  BINARY_ADD:
			a = POP(vm);
//			printf("%d \n ",a);
			b = POP(vm);
//			printf(" %d \n",b);
			PUSH(vm, a+b);
			break;

		case RETURN_VALUE:
			v = POP(vm);
			printf(" %d \n",v);
			return;
			break;
		default:
			break;
		}
	}
}while(1);

}


/* def sum1():
	a=1
        b=2
        return a+b */


/*
	2     0 LOAD_CONST               1 (1)
              3 STORE_FAST               0 (a)

  3           6 LOAD_CONST               2 (2)
              9 STORE_FAST               1 (b)

  4          12 LOAD_FAST                0 (a)
             15 LOAD_FAST                1 (b)
             18 BINARY_ADD          
             19 RETURN_VALUE   
*/


int main()
{
	int program[]={
  	0,LOAD_CONST,1,    
	3,STORE_FAST,0,    
        6,LOAD_CONST,2,   
        9,STORE_FAST,1,    
        12,LOAD_FAST,1,     
        15,LOAD_FAST,0,     
        18,BINARY_ADD,               
        19,RETURN_VALUE
};

	VM* vm = newVM(program,0,10);
	run(vm);
}





