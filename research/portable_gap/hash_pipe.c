/* Same public ABI as Linux hash_pipe.c; no copied/reordered numeric data. */
#include <stdint.h>
#include <stddef.h>
int hash_stream_begin(void **);
int hash_stream_update(void *, const double *, const int64_t *);
int hash_stream_finish(void *, char[64]);
int hash_array_checked(const double *values, const int64_t *count, char digest[64]) {
    void *stream = NULL;
    int result = hash_stream_begin(&stream);
    if (result) return result;
    result = hash_stream_update(stream, values, count);
    char discarded[64];
    int finished = hash_stream_finish(stream, result ? discarded : digest);
    return result ? result : finished;
}
