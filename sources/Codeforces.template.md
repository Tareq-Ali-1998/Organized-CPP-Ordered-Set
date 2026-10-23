Hello everyone!

After a long break from competitive programming, I’m back with something I wanted to have ready in my template: an ordered set and multiset with a clean member-function interface.

The project is **Organized C++ Ordered Set**. You can write `ordered_set<int>` or `ordered_multiset<int>`, access sorted ranks with `s[i]`, and use normal-looking bounds and erasure functions. It uses GNU PBDS with a strict comparator, including when duplicates are present.

{{repository}}

## Usage first

{{example:QuickStart}}

Every rank is **zero-based**. `s[i]` returns a read-only reference and costs $O(\log(n+1))$, not $O(1)$. Both `s[i]` and `s.at(i)` throw `out_of_range` if the rank is invalid; `find_by_order(i)` returns `end()` instead.

Use C++17 or newer with GNU libstdc++ and PBDS. GCC works; Clang works with that library. Plain MSVC does not provide these GNU headers. Keep the includes before macros such as `#define endl '\n'`.

## Two operations behind the interface

`order_of_key(x)` counts keys strictly before `x`. `find_by_order(i)` finds sorted rank `i`. PBDS maintains subtree sizes, which makes both operations logarithmic. [GCC documents these order-statistics operations here](https://gcc.gnu.org/onlinedocs/gcc-10.4.0/libstdc++/api/a10587.html).

For ascending values `{2, 5, 7, 7}`:

| Expression | Result |
|---|---:|
| `s[0]` | `2` |
| `s.order_of_key(7)` | `2` |
| `s.order_of_key_upper(7)` | `4` |
| `s.count(7)` | `2` |
| `s.first_index(7)` | `2` |
| `s.last_index(7)` | `3` |

An upper-rank operation is useful because `order_of_key(x + 1)` can overflow and does not generalize to strings or custom keys.

## Duplicates without `less_equal`

Please do not replace `less` with `less_equal` in a PBDS tree. The comparator must define a strict weak ordering; in particular, comparing a key with itself must return false. [The standard associative-container requirements use the same rule](https://eel.is/c++draft/associative.reqmts).

The multiset stores `(value, insertion ID)`. It compares values first and IDs only when the values are comparator-equivalent. The IDs are deterministic counters, not random priorities or hashes. Public iterators and indexed access expose only the value.

For example, inserting `7, 2, 7, 5` creates `(7,0), (2,1), (7,2), (5,3)`. In sorted order they become `(2,1), (5,3), (7,0), (7,2)`.

Bounds and value-rank queries walk through the existing tree metadata directly. They do not copy the searched key or manufacture sentinel pairs. The default ID is `uint64_t`; exhaustion is checked before wraparound. `clear()` resets the counter, while ordinary erasure does not.

## Interface and complexity

Let $n$ count stored occurrences, including duplicates. Let $q$ be the number erased and $m$ the number inserted in a batch. Comparisons, key operations, and comparator operations are assumed constant-cost below.

| Operation | Meaning | Time |
|---|---|---|
| `insert(x)`, `emplace(args...)` | Unique set returns `{iterator, inserted}`; multiset returns the new occurrence’s iterator | $O(\log(n+1))$ |
| `find(x)`, `contains(x)`, `count(x)` | Normal value lookup; count is logarithmic even with many duplicates | $O(\log(n+1))$ |
| `lower_bound(x)`, `upper_bound(x)`, `equal_range(x)` | Normal bounds in comparator order | $O(\log(n+1))$ |
| `order_of_key(x)`, `order_of_key_upper(x)` | Number before / before-or-equivalent to `x` | $O(\log(n+1))$ |
| `find_by_order(i)`, `s[i]`, `at(i)` | Zero-based selection | $O(\log(n+1))$ |
| `first_index(x)`, `last_index(x)` | First/last equivalent rank, or `-1` | $O(\log(n+1))$ |
| `index_of(it)` | Rank of this exact occurrence; `end()` maps to `size()` | $O(\log(n+1))$ |
| `count_range(a, b)` | Inclusive value range; reversed bounds return zero | $O(\log(n+1))$ |
| `erase_one(x)`, `erase(it)`, `erase_by_order(i)` | Remove one occurrence | $O(\log(n+1))$ |
| `erase(x)` | Remove all equivalent occurrences | Unique: $O(\log(n+1))$; multi: $O((q+1)\log(n+1))$ |
| `erase(first, last)` | Half-open iterator range | $O(1+q\log(n+1))$ |
| `insert(first, last)`, `insert({a, b})` | Insert a batch | $O(1+m\log(n+m+1))$ |
| `size()`, `empty()`, `front()`, `back()` | Size and cached endpoints; empty endpoints throw | $O(1)$ |
| `clear()` | Remove all entries and reset multiset IDs | $O(n)$ |
| Forward/reverse traversal | Read-only bidirectional iteration | $O(n)$ for a full traversal |

Bulk erasure uses individual PBDS node erasures. It does not inherit `std::multiset`’s $O(\log(n+1)+q)$ erase-by-value bound. `emplace` constructs a key and inserts it; PBDS still copies that key into its node.

Both classes support range/initializer-list construction, copying, moving, and swapping. Moves allocate an empty PBDS sentinel, so they are not `noexcept`; move assignment also destroys the destination’s previous contents. Swapping is constant-time when the comparator swap is constant-time. The repository’s API reference documents every overload, iterator rule, and exception.

## A sliding-window example

The outgoing value might have duplicates, so remove **one** copy. For a lower median, use rank `(k - 1) / 2`:

{{example:SlidingMedian}}

For `{5, 1, 5, 2, 9, 2}` and `k = 3`, this returns `{5, 2, 5, 2}`. Time is $O(n\log(k+1))$. The tree uses $O(k)$ space, apart from the returned answers.

## Details that can cost a submission

- `erase(x)` removes every copy. `erase_one(x)` removes one.
- `greater<T>` changes the meaning of “before.” Rank zero becomes the largest key, and an inclusive descending range is written in that order, such as `count_range(9, 3)`.
- Stored keys are immutable through iterators and indexing. Erase and reinsert to change a key.
- Check for `end()` before dereferencing a bound or an invalid selection.
- Use the unique set when duplicates are unnecessary. The multiset stores one ID per occurrence.

## Validation

The included reference suite exercises 384,000 randomized operations, 265,720 bounded exhaustive trace states, and 27,073,587 checks per successful full run. It compares against standard sets/multisets in both sort directions, including custom keys, numeric limits, iterator stability, copy/move/swap, and checked ID exhaustion.

The article examples and recipe algorithms are checked separately. Current compiler results and any execution restrictions are recorded in the repository’s validation report. Finite tests help find bugs; they do not turn an invalid comparator into a valid one. :)

## Complete implementation

Copy this above your solution functions. The code has no custom-header dependency when pasted as a whole.

<spoiler summary="Ordered set + multiset implementation (C++17)">

{{implementation}}

</spoiler>

{{medium}}

Thanks for reading. If you find a counterexample, please share the smallest reproducing case so it can become a regression test. <3

*By Tareq Ali. This article was organized with AI assistance.*
