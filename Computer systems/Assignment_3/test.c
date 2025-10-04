#include<stdio.h>
#include<stdlib.h>

#define align_down(x, a) ((x) & ~((typeof(x))(a) - 1))

int main(){
    unsigned long x = 0x13456;
    unsigned long a = 0x1000; // Example alignment (4096 bytes)
    unsigned long aligned_value = align_down(x, a);
    printf("Original value: 0x%lx\n", x);
    printf("Aligned value: 0x%lx\n", aligned_value);
    return 0;
}