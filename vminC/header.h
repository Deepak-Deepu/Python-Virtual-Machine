#define TRUE 1
#define FALSE 0
#define MAXVAL 2000
#define SIZE 1
#define NUM 4
#define HAVE_ARG 90
#define MAXPYC 5000

struct field {
    int val[MAXVAL];
    int length;    
};

struct code_obj {
    char* name;
    struct field code;
    struct field consts;
    struct field varnames;
    struct obj* names[10];
    int name_cnt;
};

union value {
    int intval;
    struct code_obj* pobj;
};

struct obj {
    union value val;
    char name[20];
    int type;
};

void push(int data);
int pop(void);
int get_top_n(int n);


struct obj* objects[15];

void execute(struct code_obj* pobj);
