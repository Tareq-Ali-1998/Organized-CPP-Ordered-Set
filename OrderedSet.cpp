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

using namespace std;

#define endl '\n'
#define ll long long
#define LSB __builtin_ctzll
#define MSB 63-__builtin_clzll
#define BITS __builtin_popcountll


void SolveTestCase() {

    ordered_set<int> s = {7, 2, 7, 5};
    ordered_multiset<int> ms = {7, 2, 7, 5};

    cout << s.size() << endl;
    cout << ms.size() << endl;
    cout << s[0] << endl;
    cout << ms[2] << endl;
    cout << ms.order_of_key(7) << endl;
    cout << ms.order_of_key_upper(7) << endl;
    cout << ms.count(7) << endl;
    cout << ms.count_range(5, 7) << endl;

    ms.erase_one(7);
    cout << ms.count(7) << endl;

    ms.erase(7);
    cout << ms.contains(7) << endl;

    for (int value : ms) {
        cout << value << ' ';
    }
    cout << endl;

}


int main() {

    ios_base :: sync_with_stdio(0);
    cin.tie(0);
    cout.tie(0);

    SolveTestCase();
    return 0;

}
