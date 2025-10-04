VM Assignment - Complete Answers and Analysis

1. Memory Addresses

What do you notice about the addresses printed by the two processes?

The addresses printed by both the parent and child processes are IDENTICAL:
- text:   0x5c5c788f134e
- rodata: 0x5c5c788f20c1  
- data:   0x5c5c788f4010
- bss:    0x5c5c788f4049
- heap:   0x5c5c9f4372a0
- stack:  0x7fff9927f212

Do you think the processes share the same memory? Explain why this either must be or cannot be the case.



Large Program Results:

- ./large (no arguments): Allocated 131,058 GB before failing - this demonstrates that mmap() can "allocate" enormous amounts of virtual memory without actually using physical RAM
- ./large read: Allocated and read up to 20+ GB - reading forces the OS to actually map physical pages
- ./large write: Allocated and wrote up to 6+ GB - writing is more expensive as it requires both mapping and potentially swapping

The key insight is that mmap() uses "lazy allocation" - virtual memory is allocated immediately, but physical memory is only allocated when accessed.

2. Timings

Results from timings program:
calloc():
-    call:   165 microseconds
-    loop 1: 676 microseconds  
-    loop 2: 679 microseconds
-    sum:    1520 microseconds

mmap():
-    call:    14 microseconds
-    loop 1: 819 microseconds
-    loop 2: 681 microseconds  
-    sum:    1514 microseconds

Both calloc and mmap allocate a block of zero-initialized memory. Which call takes less time?
- mmap() takes less time (14 μs vs 165 μs) because it uses lazy allocation

Which memory region is faster for the application to access, the first time it does this?
- calloc memory is faster on first access (676 μs vs 819 μs) because calloc pre-allocates and zeros the memory

Which memory region is faster for the application to access, the second time it does this?
- Both are similar on second access (679 μs vs 681 μs) because both regions are now fully mapped

What do these things imply about the work being done by calloc versus mmap?
- calloc does more work upfront (allocating and zeroing physical pages immediately)
- mmap defers the actual allocation until first access (demand paging)
- This explains why mmap's call is faster but first access is slower

Could cache misses alone account for this time difference?
- No, cache misses alone cannot account for the ~140 μs difference in first access
- The difference is primarily due to page faults and memory allocation overhead

3. Page Faults

Results from faults program:
calloc():
-     call:   26 page faults
-     loop 1:  0 page faults
-     loop 2:  0 page faults
-     sum:    26 page faults

mmap():
-     call:    0 page faults
-     loop 1: 25 page faults
-     loop 2:  0 page faults
-     sum:    25 page faults

Which allocation call results in more page faults?
- calloc results in more page faults (26 vs 0) during the allocation call itself

Which memory region incurs more page faults upon initial access?
- mmap memory incurs page faults on first access (25 page faults), while calloc memory incurs none

Compare the numbers you get from faults with the numbers you get from timings. Do the different numbers of page faults explain the different timings?
- Yes! The page fault patterns directly correlate with the timing differences:
  - calloc's 26 page faults during allocation explain its slower call time (165 μs)
  - mmap's 25 page faults during first access explain its slower first loop time (819 μs)
  - Both have similar total page faults (26 vs 25), explaining similar total times

4. Address

Results from bounds program:
Page fault at offset 0x00000 (    0)
Page fault at offset 0x01000 ( 4096)  
Page fault at offset 0x02000 ( 8192)
Page fault at offset 0x03000 (12288)

Looking at the output, how large is each page?
- Each page is 4096 bytes (4 KB). This is evident from the page fault occurring every 4096 bytes.

Which bits are part of the page offset and which are part of the page number?
- Page size = 4096 = 2^12 bytes
- Therefore, the lower 12 bits (bits 0-11) are the page offset
- The upper bits (bits 12 and above) form the page number
- In hex: 0x1000 = 4096, so the page boundary is at multiples of 0x1000

5. Invalid Access

The program invalid.c has a bug in the loop condition:
```c
for (int index = 0; index <= LENGTH; ++index)  // BUG: should be < not <=
```

What happens when you run it? Which array index is the problem?
- The program crashes with a segmentation fault
- The problem is array index 8192 (LENGTH = 8192)
- The valid indices are 0 to 8191, but the loop tries to access index 8192

What is special about the address of this array (non-)element?
- mmap returns page-aligned allocations
- The array starts at a page boundary (e.g., 0x7fffe0000000)  
- Index 8192 is exactly one page beyond the allocated region
- Since LENGTH = 8192 bytes = 2 pages, accessing index 8192 tries to write to the next unmapped page

The OS cannot always detect out-of-bounds memory accesses. There are at least two ways you could change this program that would make it appear to run normally but would not actually fix the bug. Can you think of them?

1. Allocate more memory than needed (e.g., LENGTH * 2), so the out-of-bounds access still falls within allocated memory
2. Change the mmap call to allocate an extra page, making the out-of-bounds access land in valid but unintended memory

6. Protection

Results from running protected with different permissions:

"" (no permissions): 
- Reading... Segmentation fault - cannot read from memory with no permissions

"r" (read only):
- Reading... success!
- Writing... Segmentation fault - cannot write to read-only memory

"rw" (read-write):  
- Reading... success!
- Writing... success!
- Executing... Segmentation fault - cannot execute code from non-executable memory

"rwx" (read-write-execute):
- Reading... success!
- Writing... success!  
- Executing... success! - all operations succeed with full permissions

This demonstrates that the hardware enforces memory protection at the page level. Each page has permission bits that control what operations are allowed. The operating system sets these bits when mapping memory, and the CPU hardware enforces them by generating segmentation faults for invalid operations.

Key Insights:
1. Virtual memory provides process isolation and security
2. Demand paging optimizes memory usage by delaying physical allocation
3. Page faults are the mechanism by which the OS manages memory on-demand
4. Memory protection prevents unauthorized access and code execution
5. These features work together to provide a secure, efficient memory management system
