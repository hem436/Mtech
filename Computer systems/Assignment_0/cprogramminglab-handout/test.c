#include <stdio.h>

#include "queue.c"

#include <stdlib.h>
#include <string.h>


int main() {
    queue_t *q = queue_new();
    // write test cases for each operations
    // Example test case for queue_insert_head
    if (queue_insert_head(q, "Hello")) {
        printf("Inserted %s at head\n", q->head->value);
    } else {
        printf("Failed to insert at head\n");
    }
    // Example test case for queue_insert_tail
    if (queue_insert_tail(q, "World")) {
        printf("Inserted %s at tail\n", q->tail->value);
    } else {
        printf("Failed to insert at tail\n");
    }
    // example test case for queue_remove_head
    queue_insert_head(q, "namaste");
    queue_insert_tail(q, "r");
    // Example test case for queue_size
    queue_reverse(q);
    size_t size = queue_size(q);
    printf("\nQueue size: %zu\n", size);

    char buf[5];
    int i = 0;
    while (q->head != NULL) {
        i++;
        if (i > 5) {
            printf("Infinite loop\n");
            break;
        }
        if (queue_remove_head(q, buf, sizeof(buf))) {
            printf("Removed head: %s\n with length: %zd\n", buf,strlen(buf));
        } else {
            printf("Failed to remove head\n");
        }
    }

    // Free the queue
    queue_free(q);
    // Example test case for queue_size
    size = queue_size(q);
    printf("Queue size: %zu\n", size);
    return 0;
}