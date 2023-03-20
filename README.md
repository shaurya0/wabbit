# H1 build and run command
- Install clang
- Install llvmlite with pip

`rm wabbit/print_char.so wabbit/wabbit_module.o wabbit/main; clang -shared -o wabbit/print_char.so wab
bit/print_char.c && python wabbit/main.py -f wabbit/testfile.wb --compile && clang -o wabbit/main wabbi
t/main.c wabbit/wabbit_module.o wabbit/print_char.so && ./wabbit/main`
