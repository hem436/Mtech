#include <stdio.h>
#include <stdint.h>

int main() {
    uint32_t eax, edx;
    uint8_t al;

    // Request feature report (cpuid with eax=1)
    __asm__ volatile (
        "mov $1, %%eax\n\t"
        "cpuid\n\t"
        : "=a"(eax), "=d"(edx)
        : 
        : "ebx", "ecx"
    );

    // Extract bit 0 of edx
    al = (edx & 1);

    printf("Bit 0 of edx after cpuid(eax=1): %u\n", al);
    return 0;
}