/* macOS-only SHA256 backend. Input remains exact native Fortran bytes. */
#include <CommonCrypto/CommonDigest.h>
#include <limits.h>
#include <stdint.h>
#include <stdlib.h>

struct hash_stream { CC_SHA256_CTX context; };

int hash_stream_begin(void **handle) {
    if (!handle) return 93;
    *handle = NULL;
    struct hash_stream *stream = malloc(sizeof(*stream));
    if (!stream) return 90;
    if (!CC_SHA256_Init(&stream->context)) { free(stream); return 92; }
    *handle = stream;
    return 0;
}

int hash_stream_update(void *handle, const double *values, const int64_t *count) {
    if (!handle || !count || *count < 0 ||
        (uint64_t)*count > SIZE_MAX / sizeof(double)) return 93;
    size_t remaining = (size_t)*count * sizeof(double);
    if (remaining && !values) return 93;
    const unsigned char *bytes = (const unsigned char *)values;
    struct hash_stream *stream = handle;
    while (remaining) {
        CC_LONG length = remaining > UINT_MAX ? UINT_MAX : (CC_LONG)remaining;
        if (!CC_SHA256_Update(&stream->context, bytes, length)) return 95;
        bytes += length;
        remaining -= length;
    }
    return 0;
}

int hash_stream_finish(void *handle, char digest[64]) {
    if (!handle || !digest) return 93;
    unsigned char raw[CC_SHA256_DIGEST_LENGTH];
    struct hash_stream *stream = handle;
    int ok = CC_SHA256_Final(raw, &stream->context);
    free(stream);
    if (!ok) return 96;
    const char hex[] = "0123456789abcdef";
    for (int i = 0; i < CC_SHA256_DIGEST_LENGTH; ++i) {
        digest[2*i] = hex[raw[i] >> 4];
        digest[2*i+1] = hex[raw[i] & 15];
    }
    return 0;
}
