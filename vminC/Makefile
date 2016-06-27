pyvm: my_vm.c stack.o opera_tions.o file_handling.o header.h op_code.h
	cc -g -w my_vm.c stack.o opera_tions.o file_handling.o -o my_vm
stack.o: stack.c
	gcc -g -w -c stack.c
opera_tions.o: opera_tions.c 
	gcc -g -w -c opera_tions.c
file_handling.o: file_handling.c op_code.h
	gcc -g -w -c file_handling.c    
clean:
	rm -f my_vm
	rm -f *.o
	rm -f *.gch
