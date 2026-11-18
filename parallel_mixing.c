/* cc -O3 -std=c11 -fopenmp parallel_mixing.c -o parallel_mixing */
#include <ctype.h>
#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <omp.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void fail(const char *message) {
    fprintf(stderr, "%s\n", message);
    exit(EXIT_FAILURE);
}

static void *allocate(size_t count, size_t width) {
    void *memory = calloc(count, width);
    if (!memory) fail("Insufficient memory for the permutation table or search.");
    return memory;
}

typedef struct {
    uint32_t *images;
    size_t size, capacity;
} Table;

static void append(Table *table, const char *token) {
    char *end;
    errno = 0;
    int base = token[0] == '0' && (token[1] == 'x' || token[1] == 'X') ? 16 : 10;
    uintmax_t value = strtoumax(token, &end, base);
    if (*token == '-' || *end || end == token || errno || value > UINT32_MAX)
        fail("Expected unsigned decimal or 0x-prefixed 32-bit images.");
    if (table->size == table->capacity) {
        if (table->capacity > SIZE_MAX / (2 * sizeof(uint32_t)) ||
            table->capacity > UINT32_MAX)
            fail("Table exceeds the 32-bit implementation or this host's address space.");
        size_t capacity = table->capacity ? 2 * table->capacity : 16;
        void *images = realloc(table->images, capacity * sizeof(uint32_t));
        if (!images) fail("Insufficient memory to read the permutation table.");
        table->images = images;
        table->capacity = capacity;
    }
    table->images[table->size++] = (uint32_t)value;
}

static void read_images(Table *table, FILE *stream, const char *text) {
    char token[64];
    size_t used = 0;
    for (;;) {
        int c = stream ? fgetc(stream) : (*text ? (unsigned char)*text++ : EOF);
        if (c == EOF || c == ',' || isspace(c)) {
            if (used) {
                token[used] = '\0';
                append(table, token);
                used = 0;
            }
            if (c == EOF) break;
        } else {
            if (used == sizeof(token) - 1 || c == '\0') fail("Invalid image token.");
            token[used++] = (char)c;
        }
    }
    if (stream && ferror(stream)) fail("Unable to read permutation table.");
}

static unsigned validate(const Table *table) {
    size_t n = table->size;
    if (n < 2 || (n & (n - 1))) fail("Table length must be a power of two, at least two.");
    size_t words = (n - 1) / 64 + 1;
    uint64_t *seen = allocate(words, sizeof(*seen));
    for (size_t i = 0; i < n; i++) {
        uint32_t b = table->images[i];
        uint64_t bit = UINT64_C(1) << (b % 64);
        if (b >= n || (seen[b / 64] & bit)) fail("Expected a permutation of 0 through N-1.");
        seen[b / 64] |= bit;
    }
    free(seen);
    unsigned bits = 0;
    while ((n >>= 1) != 0) bits++;
    return bits;
}

static uint32_t gcd(uint32_t a, uint32_t b) {
    while (b) {
        uint32_t remainder = a % b;
        a = b;
        b = remainder;
    }
    return a;
}

typedef struct {
    size_t reached;
    uint32_t period;
} Result;

static bool affine(const uint32_t *p, size_t n) {
    for (size_t x = 1; x < n; x++) {
        size_t bit = x & -x;
        if ((p[x] ^ p[x ^ bit]) != (p[bit] ^ p[0])) return false;
    }
    return true;
}

/* Both members of {x,x XOR a} yield the same edge. Scan its unique member
   whose least significant active bit of a is zero. */
static void add_row(const uint32_t *p, size_t n, uint32_t a, uint64_t *targets) {
    size_t bit = a & -a;
    for (size_t base = 0; base < n; base += 2 * bit) {
        for (size_t x = base; x < base + bit; x++) {
            uint32_t b = p[x] ^ p[x ^ a];
            targets[b / 64] |= UINT64_C(1) << (b % 64);
        }
    }
}

static Result classify(const Table *table, int threads, uint32_t *depth) {
    size_t n = table->size;
    const uint32_t *p = table->images;
    for (size_t a = 0; a < n; a++) depth[a] = UINT32_MAX;
    depth[1] = 0;
    Result result = {1, 0};

    if (affine(p, n)) {
        uint32_t a = 1;
        while ((a = p[a] ^ p[0]) != 1) depth[a] = (uint32_t)result.reached++;
        result.period = (uint32_t)result.reached;
        return result;
    }

    uint32_t *queue = allocate(n, sizeof(*queue));
    queue[0] = 1;
    size_t words = (n - 1) / 64 + 1;
    if ((size_t)threads > n - 1) threads = (int)(n - 1);
    if (words > SIZE_MAX / (size_t)threads) fail("Worker bitsets exceed address space.");
    uint64_t *scratch = allocate(words * (size_t)threads, sizeof(*scratch));
    for (size_t first = 0; first < result.reached;) {
        /* The frontier stays fixed while new vertices are appended to queue. */
        size_t end = result.reached;
        uint32_t next_depth = depth[queue[first]] + 1;
        size_t batch = (size_t)threads;
        while (first < end) {
            size_t count = batch < end - first ? batch : end - first;
            int workers = count < (size_t)threads ? (int)count : threads;
            memset(scratch, 0, words * (size_t)workers * sizeof(*scratch));
            #pragma omp parallel num_threads(workers) if(workers > 1)
            {
                uint64_t *local = scratch + words * (size_t)omp_get_thread_num();
                #pragma omp for schedule(static)
                for (size_t i = first; i < first + count; i++)
                    add_row(p, n, queue[i], local);
            }

            /* All rows in the batch share next_depth. Unioning their targets
               preserves both the set of discoveries and the period gcd. */
            for (size_t word = 0; word < words; word++) {
                uint64_t targets = scratch[word];
                for (int t = 1; t < workers; t++) targets |= scratch[words * (size_t)t + word];
                while (targets) {
                    unsigned offset = (unsigned)__builtin_ctzll(targets);
                    uint32_t b = (uint32_t)(word * 64 + offset);
                    targets &= targets - 1;
                    if (depth[b] == UINT32_MAX) {
                        depth[b] = next_depth;
                        queue[result.reached++] = b;
                    } else if (result.period != 1) {
                        result.period = gcd(result.period, next_depth - depth[b]);
                    }
                }
            }
            first += count;
            if (result.period == 1 && result.reached == n - 1) goto done;
            /* Double until the whole remaining frontier fits in one batch. */
            batch = batch <= (end - first) / 2 ? batch * 2 : end - first;
        }
    }
done:
    free(scratch);
    free(queue);
    return result;
}

static void report(size_t n, unsigned bits, Result r, const uint32_t *depth, bool witness) {
    bool connected = r.reached == n - 1;
    bool mixes = connected && r.period == 1;
    const char *status = !connected ? "disconnected" : mixes ? "mixing" : "periodic";
    printf("{\"bits\":%u,\"mixes\":%s,\"status\":\"%s\",\"period\":", bits, mixes ? "true" : "false", status);
    if (connected) printf("%" PRIu32, r.period);
    else fputs("null", stdout);
    if (witness && !connected) {
        fputs(",\"closed_set\":[", stdout);
        bool first = true;
        for (size_t a = 1; a < n; a++) if (depth[a] != UINT32_MAX) {
            printf("%s%zu", first ? "" : ",", a);
            first = false;
        }
        putchar(']');
    } else if (witness && !mixes) {
        uint32_t *heads = allocate(r.period, sizeof(*heads));
        uint32_t *next = allocate(n, sizeof(*next));
        for (size_t a = n - 1; a > 0; a--) {
            uint32_t group = depth[a] % r.period;
            next[a] = heads[group];
            heads[group] = (uint32_t)a;
        }
        fputs(",\"cyclic_classes\":[", stdout);
        for (uint32_t i = 0; i < r.period; i++) {
            fputs(i ? ",[" : "[", stdout);
            for (uint32_t a = heads[i]; a; a = next[a]) {
                printf("%" PRIu32, a);
                if (next[a]) putchar(',');
            }
            putchar(']');
        }
        putchar(']');
        free(heads);
        free(next);
    }
    puts("}");
}

int main(int argc, char **argv) {
    const char *path = NULL;
    int threads = omp_get_max_threads();
    bool witness = false;
    Table table = {0};
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-j") || !strcmp(argv[i], "--threads")) {
            if (++i == argc) fail("Missing thread count.");
            char *end;
            errno = 0;
            long value = strtol(argv[i], &end, 10);
            if (*end || errno || value <= 0 || value > INT_MAX) fail("Expected a positive thread count.");
            threads = (int)value;
        } else if (!strcmp(argv[i], "--witness")) witness = true;
        else if (!strcmp(argv[i], "--file")) {
            if (++i == argc || path) fail("Supply one --file argument.");
            path = argv[i];
        } else if (!strcmp(argv[i], "--help") || !strcmp(argv[i], "-h")) {
            puts("Usage: parallel_mixing [-j THREADS] [--witness] (--file PATH | IMAGE ...)\n"
                 "Images are P(0),P(1),... in decimal or 0x hex. --file - reads stdin.");
            return 0;
        } else read_images(&table, NULL, argv[i]);
    }
    if (path) {
        if (table.size) fail("Use --file or command line images.");
        FILE *input = !strcmp(path, "-") ? stdin : fopen(path, "r");
        if (!input) { perror(path); return 1; }
        read_images(&table, input, NULL);
        if (input != stdin) fclose(input);
    }
    unsigned bits = validate(&table);
    uint32_t *depth = allocate(table.size, sizeof(*depth));
    Result result = classify(&table, threads, depth);
    report(table.size, bits, result, depth, witness);
    free(depth);
    free(table.images);
    return 0;
}
