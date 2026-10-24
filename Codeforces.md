Hello everyone!

After a long break from competitive programming, I’m back with something I wanted to have ready in my template: an ordered set and multiset with a clean member-function interface.

The project is **Organized C++ Ordered Set**. You can write `ordered_set<int>` or `ordered_multiset<int>`, access sorted ranks with `s[i]`, and use normal-looking bounds and erasure functions. It uses GNU PBDS with a strict comparator, including when duplicates are present.

[Code, examples, and complete API reference](https://github.com/Tareq-Ali-1998/Organized-CPP-Ordered-Set)

[GitLab mirror](https://gitlab.com/tareqali591998/organized-cpp-ordered-set)

## Usage first

```c++
ordered_set<int> s = {7, 2, 7, 5};
ordered_multiset<int> ms = {7, 2, 7, 5};

cout << s.size() << '\n';                           // 3
cout << ms.size() << '\n';                          // 4
cout << s[0] << '\n';                               // 2
cout << ms[2] << '\n';                              // 7
cout << ms.order_of_key(7) << '\n';                 // 2
cout << ms.order_of_key_upper(7) << '\n';           // 4
cout << ms.count(7) << '\n';                        // 2
cout << ms.count_range(5, 7) << '\n';               // 3

ms.erase_one(7);
cout << ms.count(7) << '\n';                        // 1

ms.erase(7);
cout << ms.contains(7) << '\n';                     // 0

for (int value : ms) {
    cout << value << ' ';
}
cout << '\n';                                       // 2 5
```

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

```c++
vector<int> SlidingMedian(const vector<int>& v, int k) {

    if (k < 1 || (size_t)k > v.size()) {
        throw invalid_argument("Invalid window size");
    }

    ordered_multiset<int> s;
    vector<int> ans;
    for (size_t i = 0; i < v.size(); i++) {
        s.insert(v[i]);
        if (i >= (size_t)k) {
            s.erase_one(v[i - k]);
        }
        if (i + 1 >= (size_t)k) {
            ans.push_back(s[(k - 1) / 2]);
        }
    }
    return ans;

}
```

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

```c++
/*
MIT License

Copyright (c) 2026 Tareq Ali

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include <bits/stdc++.h>
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

using namespace std;


template<typename T, typename Compare>
class OrderedSet;

template<typename T, typename Compare, typename IdType>
class OrderedMultiSet;


// Shared read-only iterator: multiset users see T, never its hidden insertion ID.
namespace ordered_detail {

template<typename T, typename BaseIterator, bool Multi>
class Iterator {

private:
    BaseIterator current;

    explicit Iterator(BaseIterator it) : current(it) {

    }

    template<typename, typename>
    friend class ::OrderedSet;

    template<typename, typename, typename>
    friend class ::OrderedMultiSet;

public:
    using iterator_category = bidirectional_iterator_tag;
    using value_type = T;
    using difference_type = ptrdiff_t;
    using pointer = const T*;
    using reference = const T&;

    Iterator() = default;

    reference operator*() const {

        if constexpr (Multi) {
            return current->first;
        }
        else {
            return *current;
        }

    }

    pointer operator->() const {

        return std::addressof(**this);

    }

    Iterator& operator++() {

        ++current;
        return *this;

    }

    Iterator operator++(int) {

        Iterator old = *this;
        ++*this;
        return old;

    }

    Iterator& operator--() {

        --current;
        return *this;

    }

    Iterator operator--(int) {

        Iterator old = *this;
        --*this;
        return old;

    }

    friend bool operator==(Iterator a, Iterator b) {

        return a.current == b.current;

    }
    friend bool operator!=(Iterator a, Iterator b) {

        return !(a == b);

    }

};

}


template<typename T, typename Compare = less<T>>
class OrderedSet {

private:
    using Tree = __gnu_pbds::tree<T, __gnu_pbds::null_type, Compare,
                                __gnu_pbds::rb_tree_tag,
                                __gnu_pbds::tree_order_statistics_node_update>;

    Tree tree;

public:
    using value_type = T;
    using key_type = T;
    using key_compare = Compare;
    using size_type = typename Tree::size_type;
    using difference_type = ptrdiff_t;
    using iterator = ordered_detail::Iterator<T, typename Tree::const_iterator, false>;
    using const_iterator = iterator;
    using reverse_iterator = std::reverse_iterator<iterator>;
    using const_reverse_iterator = reverse_iterator;

    explicit OrderedSet(const Compare& compare = Compare()) : tree(compare) {

    }

    template<typename Iterator>
    OrderedSet(Iterator first, Iterator last, const Compare& compare = Compare()) : tree(compare) {

        insert(first, last);

    }

    OrderedSet(initializer_list<T> values, const Compare& compare = Compare()) : tree(compare) {

        insert(values.begin(), values.end());

    }

    OrderedSet(const OrderedSet&) = default;
    OrderedSet& operator=(const OrderedSet&) = default;

    // PBDS needs a new empty sentinel, so moving may allocate and is not noexcept.
    OrderedSet(OrderedSet&& other) : tree(other.key_comp()) {

        swap(other);

    }

    OrderedSet& operator=(OrderedSet&& other) {

        if (this != &other) {
            OrderedSet current(std::move(other));
            swap(current);
        }
        return *this;

    }

    bool empty() const {

        return tree.empty();

    }
    size_type size() const {

        return tree.size();

    }
    Compare key_comp() const {

        return tree.get_cmp_fn();

    }
    iterator begin() const {

        return iterator(tree.begin());

    }
    iterator end() const {

        return iterator(tree.end());

    }
    iterator cbegin() const {

        return begin();

    }
    iterator cend() const {

        return end();

    }
    reverse_iterator rbegin() const {

        return reverse_iterator(end());

    }
    reverse_iterator rend() const {

        return reverse_iterator(begin());

    }
    const_reverse_iterator crbegin() const {

        return rbegin();

    }
    const_reverse_iterator crend() const {

        return rend();

    }

    // Unique keys: return the existing/new iterator and whether insertion happened.
    pair<iterator, bool> insert(const T& value) {

        auto result = tree.insert(value);
        return {iterator(result.first), result.second};

    }

    void insert(initializer_list<T> values) {

        insert(values.begin(), values.end());

    }

    template<typename... Args>
    pair<iterator, bool> emplace(Args&&... args) {

        return insert(T(std::forward<Args>(args)...));

    }

    template<typename Iterator>
    void insert(Iterator first, Iterator last) {

        for (; first != last; ++first) {
            insert(*first);
        }

    }

    iterator find(const T& value) const {

        return iterator(tree.find(value));

    }
    bool contains(const T& value) const {

        return find(value) != end();

    }
    size_type count(const T& value) const {

        return contains(value);

    }
    iterator lower_bound(const T& value) const {

        return iterator(tree.lower_bound(value));

    }
    iterator upper_bound(const T& value) const {

        return iterator(tree.upper_bound(value));

    }

    pair<iterator, iterator> equal_range(const T& value) const {

        return {lower_bound(value), upper_bound(value)};

    }

    // Like multiset::erase(value), remove all equivalent occurrences and count them.
    size_type erase(const T& value) {

        return tree.erase(value);

    }
    // Remove one equivalent occurrence; useful when a sliding window has duplicates.
    bool erase_one(const T& value) {

        return tree.erase(value);

    }
    iterator erase(iterator it) {

        return iterator(tree.erase(it.current));

    }

    // Half-open iterator range. Each PBDS node erase costs O(log(size() + 1)).
    iterator erase(iterator first, iterator last) {

        while (first != last) {
            first = erase(first);
        }
        return last;

    }

    bool erase_by_order(size_type idx) {

        iterator it = find_by_order(idx);
        if (it == end()) {
            return 0;
        }
        erase(it);
        return 1;

    }

    // Zero-based sorted rank. Invalid ranks return end(), not an element.
    iterator find_by_order(size_type idx) const {

        return iterator(tree.find_by_order(idx));

    }
    size_type order_of_key(const T& value) const {

        return tree.order_of_key(value);

    }

    // Count keys before or equivalent to value without computing value + 1.
    size_type order_of_key_upper(const T& value) const {

        auto node = tree.node_begin();
        auto last = tree.node_end();
        const Compare& compare = tree.get_cmp_fn();
        size_type ans = 0;
        while (node != last) {
            if (compare(value, **node)) {
                node = node.get_l_child();
            }
            else {
                auto left = node.get_l_child();
                ans += 1 + (left == last ? 0 : left.get_metadata());
                node = node.get_r_child();
            }
        }
        return ans;

    }

    // Inclusive VALUE range in comparator order; this is not an iterator range.
    size_type count_range(const T& first, const T& last) const {

        if (tree.get_cmp_fn()(last, first)) {
            return 0;
        }
        return order_of_key_upper(last) - order_of_key(first);

    }

    // end() maps to size(); a multiset iterator identifies one exact occurrence.
    size_type index_of(iterator it) const {

        return it == end() ? size() : order_of_key(*it);

    }

    difference_type first_index(const T& value) const {

        iterator it = find(value);
        return it == end() ? -1 : (difference_type)order_of_key(value);

    }

    difference_type last_index(const T& value) const {

        return first_index(value);

    }

    // Checked, read-only rank access. Its logarithmic cost also applies to operator[].
    const T& at(size_type idx) const {

        if (idx >= size()) {
            throw out_of_range("OrderedSet index is out of range");
        }
        return *find_by_order(idx);

    }

    const T& operator[](size_type idx) const {

        return at(idx);

    }

    const T& front() const {

        if (empty()) {
            throw out_of_range("OrderedSet is empty");
        }
        return *begin();

    }

    const T& back() const {

        if (empty()) {
            throw out_of_range("OrderedSet is empty");
        }
        return *rbegin();

    }

    void clear() {

        tree.clear();

    }
    void swap(OrderedSet& other) {

        tree.swap(other.tree);

    }

    friend void swap(OrderedSet& a, OrderedSet& b) {

        a.swap(b);

    }

};


template<typename T, typename Compare = less<T>, typename IdType = uint64_t>
class OrderedMultiSet {

private:
    static_assert(is_integral_v<IdType> && is_unsigned_v<IdType> &&
                  !is_same_v<IdType, bool>, "Insertion IDs must be unsigned integers");

    using Id = IdType;
    using Entry = pair<T, Id>;

    // Keep a strict ordering: compare values first, then insertion IDs for ties.
    struct EntryCompare {

        Compare compare;

        explicit EntryCompare(const Compare& valueCompare) : compare(valueCompare) {

        }

        bool operator()(const Entry& a, const Entry& b) const {

            if (compare(a.first, b.first)) {
                return 1;
            }
            if (compare(b.first, a.first)) {
                return 0;
            }
            return a.second < b.second;

        }

    };

    using Tree = __gnu_pbds::tree<Entry, __gnu_pbds::null_type, EntryCompare,
                                __gnu_pbds::rb_tree_tag,
                                __gnu_pbds::tree_order_statistics_node_update>;
    using BaseIterator = typename Tree::const_iterator;

    Tree tree;
    Id nextId = 0;

    // One root-to-leaf walk. Upper selects < value or <= value in comparator order.
    template<bool Upper>
    typename Tree::size_type GetOrder(const T& value) const {

        auto node = tree.node_begin();
        auto last = tree.node_end();
        const Compare& compare = tree.get_cmp_fn().compare;
        typename Tree::size_type ans = 0;
        while (node != last) {
            const T& current = (**node).first;
            bool before;
            if constexpr (Upper) {
                before = !compare(value, current);
            }
            else {
                before = compare(current, value);
            }
            if (before) {
                auto left = node.get_l_child();
                ans += 1 + (left == last ? 0 : left.get_metadata());
                node = node.get_r_child();
            }
            else {
                node = node.get_l_child();
            }
        }
        return ans;

    }

    // Search using T directly; no temporary pair, sentinel key, or key copy is needed.
    template<bool Upper>
    BaseIterator GetBound(const T& value) const {

        auto node = tree.node_begin();
        auto last = tree.node_end();
        const Compare& compare = tree.get_cmp_fn().compare;
        BaseIterator ans = tree.end();
        while (node != last) {
            const T& current = (**node).first;
            bool before;
            if constexpr (Upper) {
                before = !compare(value, current);
            }
            else {
                before = compare(current, value);
            }
            if (before) {
                node = node.get_r_child();
            }
            else {
                ans = *node;
                node = node.get_l_child();
            }
        }
        return ans;

    }

public:
    using value_type = T;
    using key_type = T;
    using key_compare = Compare;
    using size_type = typename Tree::size_type;
    using difference_type = ptrdiff_t;

    using iterator = ordered_detail::Iterator<T, BaseIterator, true>;
    using const_iterator = iterator;
    using reverse_iterator = std::reverse_iterator<iterator>;
    using const_reverse_iterator = reverse_iterator;

    explicit OrderedMultiSet(const Compare& compare = Compare()) : tree(EntryCompare(compare)) {

    }

    template<typename Iterator>
    OrderedMultiSet(Iterator first, Iterator last, const Compare& compare = Compare()) : tree(EntryCompare(compare)) {

        insert(first, last);

    }

    OrderedMultiSet(initializer_list<T> values, const Compare& compare = Compare()) : tree(EntryCompare(compare)) {

        insert(values.begin(), values.end());

    }

    OrderedMultiSet(const OrderedMultiSet&) = default;

    OrderedMultiSet& operator=(const OrderedMultiSet& other) {

        if (this != &other) {
            OrderedMultiSet current(other);
            swap(current);
        }
        return *this;

    }

    // Transfer the tree and ID state together; the source becomes empty and reusable.
    OrderedMultiSet(OrderedMultiSet&& other) : tree(EntryCompare(other.key_comp())) {

        swap(other);

    }

    OrderedMultiSet& operator=(OrderedMultiSet&& other) {

        if (this != &other) {
            OrderedMultiSet current(std::move(other));
            swap(current);
        }
        return *this;

    }

    bool empty() const {

        return tree.empty();

    }
    size_type size() const {

        return tree.size();

    }
    Compare key_comp() const {

        return tree.get_cmp_fn().compare;

    }
    iterator begin() const {

        return iterator(tree.begin());

    }
    iterator end() const {

        return iterator(tree.end());

    }
    iterator cbegin() const {

        return begin();

    }
    iterator cend() const {

        return end();

    }
    reverse_iterator rbegin() const {

        return reverse_iterator(end());

    }
    reverse_iterator rend() const {

        return reverse_iterator(begin());

    }
    const_reverse_iterator crbegin() const {

        return rbegin();

    }
    const_reverse_iterator crend() const {

        return rend();

    }

    // Every occurrence gets a distinct ID; reject exhaustion before any wraparound.
    iterator insert(const T& value) {

        if (nextId == numeric_limits<Id>::max()) {
            throw length_error("OrderedMultiSet insertion IDs are exhausted");
        }
        auto result = tree.insert({value, nextId});
        nextId++;
        return iterator(result.first);

    }

    void insert(initializer_list<T> values) {

        insert(values.begin(), values.end());

    }

    template<typename... Args>
    iterator emplace(Args&&... args) {

        return insert(T(std::forward<Args>(args)...));

    }

    template<typename Iterator>
    void insert(Iterator first, Iterator last) {

        for (; first != last; ++first) {
            insert(*first);
        }

    }

    iterator lower_bound(const T& value) const {

        return iterator(GetBound<false>(value));

    }
    iterator upper_bound(const T& value) const {

        return iterator(GetBound<true>(value));

    }

    iterator find(const T& value) const {

        iterator it = lower_bound(value);
        if (it == end() || tree.get_cmp_fn().compare(value, *it)) {
            return end();
        }
        return it;

    }

    bool contains(const T& value) const {

        return find(value) != end();

    }
    size_type order_of_key(const T& value) const {

        return GetOrder<false>(value);

    }
    // Count keys before or equivalent to value without computing value + 1.
    size_type order_of_key_upper(const T& value) const {

        return GetOrder<true>(value);

    }

    size_type count(const T& value) const {

        return order_of_key_upper(value) - order_of_key(value);

    }

    // Inclusive VALUE range in comparator order; this is not an iterator range.
    size_type count_range(const T& first, const T& last) const {

        if (tree.get_cmp_fn().compare(last, first)) {
            return 0;
        }
        return order_of_key_upper(last) - order_of_key(first);

    }

    pair<iterator, iterator> equal_range(const T& value) const {

        return {lower_bound(value), upper_bound(value)};

    }

    iterator erase(iterator it) {

        return iterator(tree.erase(it.current));

    }

    // Half-open iterator range. Each PBDS node erase costs O(log(size() + 1)).
    iterator erase(iterator first, iterator last) {

        while (first != last) {
            first = erase(first);
        }
        return last;

    }

    // Remove one equivalent occurrence; useful when a sliding window has duplicates.
    bool erase_one(const T& value) {

        iterator it = find(value);
        if (it == end()) {
            return 0;
        }
        erase(it);
        return 1;

    }

    // Like multiset::erase(value), remove all equivalent occurrences and count them.
    size_type erase(const T& value) {

        auto range = equal_range(value);
        size_type ans = 0;
        while (range.first != range.second) {
            range.first = erase(range.first);
            ans++;
        }
        return ans;

    }

    bool erase_by_order(size_type idx) {

        iterator it = find_by_order(idx);
        if (it == end()) {
            return 0;
        }
        erase(it);
        return 1;

    }

    // Zero-based sorted rank. Invalid ranks return end(), not an element.
    iterator find_by_order(size_type idx) const {

        return iterator(tree.find_by_order(idx));

    }

    // end() maps to size(); a multiset iterator identifies one exact occurrence.
    size_type index_of(iterator it) const {

        return it == end() ? size() : tree.order_of_key(*it.current);

    }

    difference_type first_index(const T& value) const {

        iterator it = find(value);
        return it == end() ? -1 : (difference_type)order_of_key(value);

    }

    difference_type last_index(const T& value) const {

        iterator it = find(value);
        return it == end() ? -1 : (difference_type)order_of_key_upper(value) - 1;

    }

    // Checked, read-only rank access. Its logarithmic cost also applies to operator[].
    const T& at(size_type idx) const {

        if (idx >= size()) {
            throw out_of_range("OrderedMultiSet index is out of range");
        }
        return *find_by_order(idx);

    }

    const T& operator[](size_type idx) const {

        return at(idx);

    }

    const T& front() const {

        if (empty()) {
            throw out_of_range("OrderedMultiSet is empty");
        }
        return *begin();

    }

    const T& back() const {

        if (empty()) {
            throw out_of_range("OrderedMultiSet is empty");
        }
        return *rbegin();

    }

    void clear() {

        tree.clear();
        nextId = 0;

    }

    void swap(OrderedMultiSet& other) {

        tree.swap(other.tree);
        std::swap(nextId, other.nextId);

    }

    friend void swap(OrderedMultiSet& a, OrderedMultiSet& b) {

        a.swap(b);

    }

};


template<typename T, typename Compare = less<T>>
using ordered_set = OrderedSet<T, Compare>;

template<typename T, typename Compare = less<T>, typename IdType = uint64_t>
using ordered_multiset = OrderedMultiSet<T, Compare, IdType>;

template<typename T, typename Compare = less<T>, typename IdType = uint64_t>
using multi_ordered_set = OrderedMultiSet<T, Compare, IdType>;
```

</spoiler>

## Visual walkthrough

For a step-by-step explanation, the companion website lets you change values and follow rank/select queries through a tree.

[Try the interactive tree on the website](https://tareq-ali-1998.github.io/Organized-CPP-Ordered-Set/#ordered-set-lab)



[Read the detailed visual walkthrough on Medium](https://medium.com/@tareqali591998/c-ordered-set-and-multiset-a-practical-guide-to-gnu-pbds-35aeb7df7efc)

Thanks for reading. If you find a counterexample, please share the smallest reproducing case so it can become a regression test. <3

*By Tareq Ali. This article was organized with AI assistance.*
