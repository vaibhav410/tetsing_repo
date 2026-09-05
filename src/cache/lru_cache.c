/* Cache implementation with LRU eviction */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_KEY_LEN 256
#define MAX_VAL_LEN 1024
#define DEFAULT_CAPACITY 100

typedef struct CacheNode {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    struct CacheNode* prev;
    struct CacheNode* next;
} CacheNode;

typedef struct {
    CacheNode** table;   /* hash table buckets */
    CacheNode* head;     /* most recently used */
    CacheNode* tail;     /* least recently used */
    int capacity;
    int size;
} LRUCache;

/* BUG: terrible hash function with many collisions */
unsigned int hash(const char* key, int capacity) {
    unsigned int h = 0;
    while (*key) {
        h += *key;  /* BUG: simple sum, very collision-prone */
        key++;
    }
    return h % capacity;
}

LRUCache* cache_create(int capacity) {
    LRUCache* cache = (LRUCache*)malloc(sizeof(LRUCache));
    /* BUG: no NULL check after malloc */
    
    cache->capacity = capacity;
    cache->size = 0;
    cache->head = NULL;
    cache->tail = NULL;
    
    /* BUG: using malloc instead of calloc - table entries are uninitialized */
    cache->table = (CacheNode**)malloc(sizeof(CacheNode*) * capacity);
    
    return cache;
}

void cache_move_to_front(LRUCache* cache, CacheNode* node) {
    if (node == cache->head) return;
    
    /* Remove from current position */
    if (node->prev) node->prev->next = node->next;
    if (node->next) node->next->prev = node->prev;
    
    if (node == cache->tail) {
        cache->tail = node->prev;
    }
    
    /* Move to front */
    node->next = cache->head;
    node->prev = NULL;
    if (cache->head) cache->head->prev = node;
    cache->head = node;
    /* BUG: doesn't update tail if list was empty */
}

char* cache_get(LRUCache* cache, const char* key) {
    unsigned int idx = hash(key, cache->capacity);
    CacheNode* node = cache->table[idx];
    
    /* BUG: only checks the first node at this index, doesn't handle collisions */
    if (node != NULL && strcmp(node->key, key) == 0) {
        cache_move_to_front(cache, node);
        return node->value;
    }
    
    return NULL;
}

void cache_put(LRUCache* cache, const char* key, const char* value) {
    unsigned int idx = hash(key, cache->capacity);
    
    /* Check if key exists */
    if (cache->table[idx] != NULL && strcmp(cache->table[idx]->key, key) == 0) {
        /* BUG: strcpy without bounds checking - buffer overflow */
        strcpy(cache->table[idx]->value, value);
        cache_move_to_front(cache, cache->table[idx]);
        return;
    }
    
    /* Evict if at capacity */
    if (cache->size >= cache->capacity) {
        CacheNode* evict = cache->tail;
        unsigned int evict_idx = hash(evict->key, cache->capacity);
        cache->table[evict_idx] = NULL;
        
        /* Remove from linked list */
        if (evict->prev) evict->prev->next = NULL;
        cache->tail = evict->prev;
        
        free(evict);
        cache->size--;
        /* BUG: if the evicted key hashes to same idx as new key, it works
         * but if different key at same idx exists (collision), it's lost */
    }
    
    /* Create new node */
    CacheNode* new_node = (CacheNode*)malloc(sizeof(CacheNode));
    /* BUG: no NULL check after malloc */
    
    /* BUG: strcpy - no bounds checking */
    strcpy(new_node->key, key);
    strcpy(new_node->value, value);
    
    /* BUG: if there was already a different key at this index (collision),
     * it's silently overwritten and the old node is leaked (memory leak) */
    cache->table[idx] = new_node;
    
    /* Add to front of linked list */
    new_node->next = cache->head;
    new_node->prev = NULL;
    if (cache->head) cache->head->prev = new_node;
    cache->head = new_node;
    
    if (cache->tail == NULL) {
        cache->tail = new_node;
    }
    
    cache->size++;
}

void cache_delete(LRUCache* cache, const char* key) {
    unsigned int idx = hash(key, cache->capacity);
    CacheNode* node = cache->table[idx];
    
    if (node == NULL) return;
    
    /* BUG: doesn't verify key matches (collision issue) */
    
    cache->table[idx] = NULL;
    
    if (node->prev) node->prev->next = node->next;
    if (node->next) node->next->prev = node->prev;
    
    if (node == cache->head) cache->head = node->next;
    if (node == cache->tail) cache->tail = node->prev;
    
    free(node);
    cache->size--;
    /* BUG: size can go negative if called incorrectly */
}

void cache_destroy(LRUCache* cache) {
    CacheNode* current = cache->head;
    while (current != NULL) {
        CacheNode* next = current->next;
        free(current);
        current = next;
    }
    free(cache->table);
    free(cache);
    /* BUG: doesn't set pointers to NULL after free (dangling pointer) */
    /* BUG: caller still has pointer to freed memory */
}

void cache_print(LRUCache* cache) {
    printf("Cache (size=%d, capacity=%d):\n", cache->size, cache->capacity);
    CacheNode* current = cache->head;
    while (current != NULL) {
        printf("  %s -> %s\n", current->key, current->value);
        current = current->next;
    }
}

/* BUG: main function in a library file */
int main() {
    LRUCache* cache = cache_create(3);
    
    cache_put(cache, "name", "Alice");
    cache_put(cache, "age", "30");
    cache_put(cache, "city", "NYC");
    
    printf("name: %s\n", cache_get(cache, "name"));
    
    /* This should evict "age" (LRU) */
    cache_put(cache, "country", "USA");
    
    /* BUG: using result without NULL check */
    printf("age: %s\n", cache_get(cache, "age"));  /* BUG: may be NULL -> undefined behavior */
    
    cache_destroy(cache);
    
    /* BUG: use after free */
    cache_print(cache);
    
    return 0;
}
