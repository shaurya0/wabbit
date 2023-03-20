My implementation of a compiler for the wabbit language as taught in the course http://dabeaz.com/compiler.html. The implementation was written over 5 days and can compile a subset of wabbit programs to native code with the use of the [llvmlite](https://github.com/numba/llvmlite) library

### Build and run command
- Install clang
- Install llvmlite with pip

`rm wabbit/print_char.so wabbit/wabbit_module.o wabbit/main; clang -shared -o wabbit/print_char.so wab
bit/print_char.c && python wabbit/main.py -f wabbit/testfile.wb --compile && clang -o wabbit/main wabbi
t/main.c wabbit/wabbit_module.o wabbit/print_char.so && ./wabbit/main`
