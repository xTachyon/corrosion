#include <cstdio>

extern "C" unsigned f(unsigned x, unsigned y);

int main() { printf("%u\n", f(3, 2)); }