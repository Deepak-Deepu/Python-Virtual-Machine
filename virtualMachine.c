#include<stdio.h>
#include<stdlib.h>

#define PUSH(vm, v) vm->stack[++vm->sp] = v
#define POP(vm)     vm->stack[vm->sp--]
#define NCODE(vm)   vm->code[vm->pc++]

#define STACK_SIZE 100
int k=0,j=0,l=0;


	 char co_varnames[] = {'a','b'};
         char co_names[] = {};
         int co_consts[] = {0,1,2};


enum {
        LOAD_CONST = 1,
        STORE_FAST = 2,
        LOAD_FAST  = 3,
        BINARY_ADD = 4,
        RETURN_VALUE = 5
};



typedef struct {
	int* loacls; // local scoped data
	int* code;   // array od byte codes to be executed
	int* stack;  // virtual stack
	int pc;	     // program counter (aka IP - instruction pointer)
	int sp;      // stack pointer
	}VM;

VM* newVM(int* code,	// pointer to table containing a bytecode to be executed
 int pc,		// address of instruction to be invoked as first one - entrypoint/main func
 int datasize)		// total locals size required to perform a program operation
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
		int opcode = NCODE(vm);
		int v, a=0,b=0;
//		printf(" %d",opcode);
		switch(opcode)
		{
		case LOAD_CONST:
			k++;
			v=co_consts[k];
//			printf(" %d %d  \n",v,k);
//			printf(" %d ",co_consts[k]);
			PUSH(vm, co_consts[k]);
			break;
		case STORE_FAST:
			v=POP(vm);
			co_varnames[j]=v;
			j++;
			break;
		case LOAD_FAST:
//			printf("%d ",co_varnames[l]);
			PUSH(vm, co_varnames[l]);
			l++;
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
		}
}while(1);

}


/* def sum1():
        a=1
        b=2
        return a+b */

/* dis.dis(sum1)
   2	      0   LOAD_CONST               1
              3   STORE_FAST               0 

   3          6   LOAD_CONST               2 
              9   STORE_FAST               1 

   4         12   LOAD_FAST                0 
             15   LOAD_FAST                1 
             18   BINARY_ADD                 
             19   RETURN_VALUE               

*/

int main()
{
	int program[] = {
              LOAD_CONST,    
               STORE_FAST,    

               LOAD_CONST,   
              STORE_FAST,   

              LOAD_FAST,    
              LOAD_FAST,    
              BINARY_ADD,                 
              RETURN_VALUE               
};

	VM* vm = newVM(program,0,10);
	run(vm);
}



