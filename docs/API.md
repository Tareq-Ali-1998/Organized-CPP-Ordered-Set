# Function reference

The functions below belong to both containers unless a difference is stated. `n` is the current number of occurrences, `m` is the number of incoming values, and `q` is the number erased. Bounds are worst-case, assuming constant-cost key comparisons/copies and comparator operations. For expensive keys, include those costs as well.

### Construction, assignment, and types

The following forms use `C` for either container type:

| Form | Meaning | Time |
|---|---|---|
| `C s;` | Empty container with a default-constructed comparator | `O(1)` plus allocation |
| `C s(compare);` | Empty container with the supplied comparator | `O(1)` plus allocation |
| `C s(first, last, compare);` | Insert values from the half-open input range; comparator is optional | `O(m log(m + 1))` |
| `C s({a, b, c}, compare);` | Insert an initializer list; comparator is optional | `O(m log(m + 1))` |
| `C b(a);` | Independent copy, including comparator and multiset ID state | `O(n)` |
| `b = a;` | Replace `b` with an independent copy of `a`; return `b` by reference | `O(a.size() + b.size())` |
| `C b(move(a));` | Transfer storage; `a` becomes empty and reusable | `O(1)` plus allocation |
| `b = move(a);` | Transfer storage and clear the previous contents of `b`; return `b` by reference | `O(b.size())` plus allocation |
| End of lifetime | Destroy the container and its remaining keys | `O(n)` |

Copy and move self-assignment are supported. The move operations create an empty PBDS sentinel before swapping, so they can allocate and are **not `noexcept`**. An outer `vector<C>` may choose copying during reallocation; reserving its capacity can matter.

Both classes expose `value_type` and `key_type` (`T`), `key_compare` (`Compare`), unsigned `size_type`, signed `difference_type`, and the iterator aliases `iterator`, `const_iterator`, `reverse_iterator`, `const_reverse_iterator`. The const and non-const iterator aliases are the same read-only iterator type. Iterators also provide the usual `iterator_category`, `value_type`, `difference_type`, `pointer`, and `reference` traits.

### Inserting values

| Call | Return value and behavior | Time |
|---|---|---|
| `s.insert(x)` | Unique set: `pair<iterator, bool>`; bool says whether a new key was inserted. Multiset: iterator to the new occurrence | `O(log(n + 1))` |
| `s.insert(first, last)` | `void`; insert each value in the half-open input range | `O(m log(n + m + 1))` |
| `s.insert({a, b, c})` | `void`; insert each value in the list | `O(m log(n + m + 1))` |
| `s.emplace(args...)` | Construct `T(args...)`, then insert it; same return type as single-value `insert` | `O(log(n + 1))` plus construction |

For a unique set, inserting an equivalent key returns the existing element and `false`. Range insertion does not report an individual result for every value. Use a valid input range from a different container, not from the destination itself.

`emplace` is a convenience here, not a promise of in-place node construction. PBDS still copies the constructed key into its node. Batch insertion can leave earlier values inserted if a later operation throws.

### Finding values and bounds

| Call | Result | Time |
|---|---|---|
| `s.find(x)` | Iterator to an equivalent key, or `end()`; the multiset returns the first occurrence | `O(log(n + 1))` |
| `s.contains(x)` | `bool`: whether an equivalent key exists | `O(log(n + 1))` |
| `s.count(x)` | `size_type`: number of equivalent keys; zero or one for a unique set | `O(log(n + 1))` |
| `s.lower_bound(x)` | Iterator to the first key that does not come before `x`, or `end()` | `O(log(n + 1))` |
| `s.upper_bound(x)` | Iterator to the first key strictly after `x`, or `end()` | `O(log(n + 1))` |
| `s.equal_range(x)` | `pair<iterator, iterator>`: `{lower_bound(x), upper_bound(x)}` | `O(log(n + 1))` |

With the default ascending order, `lower_bound(x)` means first value `>= x` and `upper_bound(x)` means first value `> x`. If `x` is absent, both bounds are the same. The range returned by `equal_range` is half-open.

### Ranks, indexing, and counts

| Call | Result | Time |
|---|---|---|
| `s.order_of_key(x)` | `size_type`: number of keys strictly before `x` | `O(log(n + 1))` |
| `s.order_of_key_upper(x)` | `size_type`: number before or equivalent to `x` | `O(log(n + 1))` |
| `s.find_by_order(i)` | Iterator at rank `i`; `end()` when `i >= size()` | `O(log(n + 1))` |
| `s[i]` | `const T&` at rank `i`; throws `out_of_range` if invalid | `O(log(n + 1))` |
| `s.at(i)` | Same checked access and return type as `s[i]` | `O(log(n + 1))` |
| `s.first_index(x)` | Signed rank of the first equivalent key; `-1` if absent | `O(log(n + 1))` |
| `s.last_index(x)` | Signed rank of the last equivalent key; `-1` if absent | `O(log(n + 1))` |
| `s.index_of(it)` | Exact rank of that occurrence; `index_of(end()) == size()` | `O(log(n + 1))` |
| `s.count_range(a, b)` | Number of keys in the **inclusive value range** from `a` through `b`; zero for reversed bounds in comparator order | `O(log(n + 1))` |

`first_index` and `last_index` are identical in a unique set. In a multiset, `index_of(it)` uses the hidden ID, so it can distinguish equivalent occurrences. Their ranks can change after insertions and erasures even while their iterators remain valid.

Use this table for ascending order, with `L = s.order_of_key(x)` and `R = s.order_of_key_upper(x)`:

| Desired count | Expression |
|---|---|
| `< x` | `L` |
| `<= x` | `R` |
| `== x` | `R - L` |
| `> x` | `s.size() - R` |
| `>= x` | `s.size() - L` |

For an inclusive range with `a <= b`, use `s.order_of_key_upper(b) - s.order_of_key(a)`. `count_range` also checks for reversed bounds.

Do not replace the upper rank with `order_of_key(x + 1)`. `x + 1` can overflow at the maximum integer and makes no sense for a string or an arbitrary custom key. The upper-rank operation works directly with the comparator.

### Erasing values

| Call | Return value and behavior | Time |
|---|---|---|
| `s.erase_one(x)` | `bool`: remove one equivalent occurrence if present; multiset removes the first one | `O(log(n + 1))` |
| `s.erase(x)` | `size_type`: remove **all** equivalent occurrences and return how many | Unique: `O(log(n + 1))`; multi: `O((q + 1) log(n + 1))` |
| `s.erase(it)` | Remove that exact occurrence and return its successor; `end()` is a no-op returning `end()` | `O(log(n + 1))` |
| `s.erase(first, last)` | Remove the half-open iterator range and return `last` | `O(q log(n + 1))` |
| `s.erase_by_order(i)` | `bool`: remove rank `i`; false if it does not exist | `O(log(n + 1))` |
| `s.clear()` | `void`: remove everything and reset the multiset ID counter | `O(n)` |

**`erase(x)` and `erase_one(x)` are intentionally different.** In a sliding window, you usually want `erase_one`. Erasing every copy of the outgoing value would shrink the window incorrectly.

Bulk erasure performs individual PBDS node erasures. Do not give it the standard multiset's `O(log(n + 1) + q)` complexity by accident. Iterator arguments must belong to this container, and `[first, last)` must be a valid ordered range.

### Size, endpoints, comparator, and swapping

| Call | Result | Time |
|---|---|---|
| `s.size()` | `size_type`: number of stored occurrences | `O(1)` |
| `s.empty()` | `bool`: whether size is zero | `O(1)` |
| `s.front()` | `const T&`: first value in comparator order | `O(1)` |
| `s.back()` | `const T&`: last value in comparator order | `O(1)` |
| `s.key_comp()` | A copy of the comparator | Comparator copy cost |
| `s.swap(other)` | `void`: exchange trees, comparators, and multiset ID state | `O(1)` with constant-time comparator swap |
| `swap(a, b)` | `void`: the same exchange through the friend overload | Same as member `swap` |

Both `front()` and `back()` throw `out_of_range` on an empty container. The GNU tree caches its first and last nodes, which makes these endpoint operations constant time. Swapping requires the same full container type, including comparator and ID type. If comparator operations can throw, swapping should not be assumed to provide a strong exception guarantee.

### Iteration

| Call or operation | Meaning |
|---|---|
| `begin()`, `end()` | First element and past-the-end forward sentinel |
| `cbegin()`, `cend()` | The same read-only forward iterators |
| `rbegin()`, `rend()` | First reverse element and reverse sentinel |
| `crbegin()`, `crend()` | The same read-only reverse iterators |
| `*it`, `it->member` | Read the current key; never expose the hidden ID |
| `++it`, `it++`, `--it`, `it--` | Move forward/backward; postfix returns the previous iterator |
| `a == b`, `a != b` | Compare iterators from the same sequence |
| `iterator it;` | Default construction; assign a valid iterator before using it |

Getting an endpoint or dereferencing a valid iterator is constant time. A single iterator step can take `O(log(n + 1))` in the worst case; a full forward or reverse traversal takes `O(n)`. There is no `it + i`, `it[i]`, or iterator subtraction. To jump by sorted rank, use `find_by_order`.

Insertions preserve existing element iterators and references. Erasing invalidates only the erased elements; `clear` and destruction invalidate all of them. Swapping or moving transfers element iterators with their elements to the receiving container. Reacquire end iterators after those operations. As usual, do not dereference an end iterator, increment `end()`, or decrement `begin()`.

All keys are read-only, even when the container itself is mutable. `s[0] = 10` and `*s.begin() = 10` are compile errors. To change a value, erase it and insert the replacement. This keeps the tree sorted.

