#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <stdint.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <math.h>
#include <sys/time.h> 

static size_t page_size;
static void *last_mapped_page = NULL;

// align_down - rounds a value down to an alignment
// @x: the value
// @a: the alignment (must be power of 2)
//
// Returns an aligned value.
#define align_down(x, a) ((x) & ~((typeof(x))(a) - 1))
#define PAGE_ENT page_size/sizeof(double) // number of entries in a page of double
#define AS_LIMIT  (1 << 25) // Maximum limit on virtual memory bytes
#define MAX_SQRTS (1 << 27) // Maximum limit on sqrt table entries
static double *sqrts;

// Use this helper function as an oracle for square root values.
static void
calculate_sqrts(double *sqrt_pos, int start, int nr)
{
  int i;

  for (i = 0; i < nr; i++)
    sqrt_pos[i] = sqrt((double)(start + i));
}

static void
handle_sigsegv(int sig, siginfo_t *si, void *ctx)
{
  // Your code here.
  uintptr_t fault_addr = (uintptr_t)si->si_addr;

  uintptr_t page_start = align_down(fault_addr, page_size);
  // value from which need to make sqrt table
  double value = (double)((page_start - (uintptr_t)sqrts)/sizeof(double));
  // Unmap the previous page to save RAM and stay within limits
  if (last_mapped_page != NULL && last_mapped_page != (void*)page_start) {
    if (munmap(last_mapped_page, page_size) == -1) {
      fprintf(stderr, "Failed to unmap previous page at %p: %s\n", 
              last_mapped_page, strerror(errno));
    } 
  }
  void *mapped = mmap((void*)page_start, page_size, PROT_READ | PROT_WRITE,
                      MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0);
  if (mapped==MAP_FAILED){
    printf("mmap failed\n");
    exit(EXIT_FAILURE);
  }

  last_mapped_page = mapped;
  calculate_sqrts(mapped,value,PAGE_ENT);

}
static void
setup_sqrt_region(void)
{
  struct rlimit lim = {AS_LIMIT, AS_LIMIT};
  struct sigaction act;

  // Only mapping to find a safe location for the table.
  sqrts = mmap(NULL, MAX_SQRTS * sizeof(double) + AS_LIMIT, PROT_NONE,
              MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  if (sqrts == MAP_FAILED) {
    fprintf(stderr, "Couldn't mmap() region for sqrt table; %s\n",strerror(errno));
    exit(EXIT_FAILURE);
  }

  // Now release the virtual memory to remain under the rlimit.
  if (munmap(sqrts, MAX_SQRTS * sizeof(double) + AS_LIMIT) == -1) {
    fprintf(stderr, "Couldn't munmap() region for sqrt table; %s\n",
            strerror(errno));
    exit(EXIT_FAILURE);
  }

  // Set a soft rlimit on virtual address-space bytes.
  if (setrlimit(RLIMIT_AS, &lim) == -1) {
    fprintf(stderr, "Couldn't set rlimit on RLIMIT_AS; %s\n", strerror(errno));
    exit(EXIT_FAILURE);
  }

  // Register a signal handler to capture SIGSEGV.
  act.sa_sigaction = handle_sigsegv;
  act.sa_flags = SA_SIGINFO;
  sigemptyset(&act.sa_mask);
  if (sigaction(SIGSEGV, &act, NULL) == -1) {
    fprintf(stderr, "Couldn't set up SIGSEGV handler;, %s\n", strerror(errno));
    exit(EXIT_FAILURE);
  }
}

static void
test_sqrt_region(void)
{
  int i, pos = rand() % (MAX_SQRTS - 1);
  double correct_sqrt;
  struct timeval start_time, end_time;
  double elapsed_time;

  printf("Validating square root table contents...\n");
  
  // Start timing
  gettimeofday(&start_time, NULL);
  
  srand(0xDEADBEEF);

  for (i = 0; i < 500000; i++) {
    if (i % 2 == 0){
      pos = rand() % (MAX_SQRTS - 1);
    }
    else
      pos += 1;
    printf("The index is %d with value %d\n", i,pos);
    calculate_sqrts(&correct_sqrt, pos, 1);
    if (sqrts[pos] != correct_sqrt) {
      fprintf(stderr, "Square root is incorrect. Expected %f, got %f.\n",
              correct_sqrt, sqrts[pos]);
      exit(EXIT_FAILURE);
    }
  }

  // End timing
  gettimeofday(&end_time, NULL);
  
  // Calculate elapsed time in seconds
  elapsed_time = (end_time.tv_sec - start_time.tv_sec) + 
                 (end_time.tv_usec - start_time.tv_usec) / 1000000.0;

  printf("All tests passed!\n");
  printf("Testing completed in %.6f seconds\n", elapsed_time);
  printf("Average time per access: %.6f microseconds\n", 
         (elapsed_time * 1000000.0) / 500000);
}

int
main(int argc, char *argv[])
{
  page_size = sysconf(_SC_PAGESIZE);
  printf("page_size is %ld\n", page_size);
  setup_sqrt_region();
  test_sqrt_region();
  return 0;
}
