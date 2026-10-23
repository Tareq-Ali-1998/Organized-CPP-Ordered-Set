#include <bits/stdc++.h>
#include "../OrderedSet.hpp"

using namespace std;

#define endl '\n'
#define ll long long
#define LSB __builtin_ctzll
#define MSB 63-__builtin_clzll
#define BITS __builtin_popcountll


ll checks = 0;
ll operations = 0;
ll exhaustiveStates = 0;


void Check(bool ok, const char* message) {

    checks++;
    if (!ok) {
        throw runtime_error(message);
    }

}


template<typename Function>
void CheckOutOfRange(Function function) {

    bool caught = 0;
    try {
        function();
    }
    catch (const out_of_range&) {
        caught = 1;
    }
    Check(caught, "Expected out_of_range");

}


template<typename Set, typename Model>
void Validate(const Set& s, const Model& model) {

    using T = typename Set::value_type;
    vector<T> expected(model.begin(), model.end());
    Check(s.size() == model.size(), "Size differs");
    Check(s.empty() == model.empty(), "Empty differs");
    Check(vector<T>(s.begin(), s.end()) == expected, "Forward iteration differs");
    Check(vector<T>(s.cbegin(), s.cend()) == expected, "Const iteration differs");
    vector<T> reversed(expected.rbegin(), expected.rend());
    Check(vector<T>(s.rbegin(), s.rend()) == reversed, "Reverse iteration differs");
    Check(vector<T>(s.crbegin(), s.crend()) == reversed, "Const reverse iteration differs");
    Check(s.index_of(s.end()) == s.size(), "End rank differs");
    Check(s.find_by_order(s.size()) == s.end(), "Out-of-range select differs");
    Check(s.find_by_order(numeric_limits<size_t>::max()) == s.end(), "Huge select differs");
    for (size_t i = 0; i < expected.size(); i++) {
        Check(s[i] == expected[i], "Indexing differs");
        Check(s.at(i) == expected[i], "Checked indexing differs");
        auto it = s.find_by_order(i);
        Check(it != s.end() && *it == expected[i], "Select differs");
        Check(s.index_of(it) == i, "Iterator rank differs");
    }

    if (!expected.empty()) {
        Check(s.front() == expected.front(), "Front differs");
        Check(s.back() == expected.back(), "Back differs");
        auto it = s.begin();
        auto old = it++;
        Check(*old == expected.front(), "Post-increment differs");
        it = s.end();
        auto previousEnd = it--;
        Check(previousEnd == s.end() && *it == expected.back(), "Post-decrement differs");
        Check(*--s.end() == expected.back(), "Decrement end differs");
    }

    auto compare = model.key_comp();
    for (int value = -27; value <= 27; value += 3) {
        auto first = model.lower_bound(value);
        auto last = model.upper_bound(value);
        size_t lower = distance(model.begin(), first);
        size_t upper = distance(model.begin(), last);
        Check(s.order_of_key(value) == lower, "Lower rank differs");
        Check(s.order_of_key_upper(value) == upper, "Upper rank differs");
        Check(s.count(value) == upper - lower, "Count differs");
        Check(s.contains(value) == (lower != upper), "Contains differs");
        Check((s.find(value) == s.end()) == (first == last), "Find differs");
        auto actualLower = s.lower_bound(value);
        auto actualUpper = s.upper_bound(value);
        Check((actualLower == s.end()) == (first == model.end()), "Lower bound end differs");
        Check((actualUpper == s.end()) == (last == model.end()), "Upper bound end differs");
        if (first != model.end()) {
            Check(*actualLower == *first, "Lower bound differs");
        }
        if (last != model.end()) {
            Check(*actualUpper == *last, "Upper bound differs");
        }
        auto range = s.equal_range(value);
        Check(range.first == actualLower && range.second == actualUpper, "Equal range differs");
        ptrdiff_t firstIdx = lower == upper ? -1 : (ptrdiff_t)lower;
        ptrdiff_t lastIdx = lower == upper ? -1 : (ptrdiff_t)upper - 1;
        Check(s.first_index(value) == firstIdx, "First index differs");
        Check(s.last_index(value) == lastIdx, "Last index differs");
        for (int other : {-30, 0, 30}) {
            size_t count = 0;
            if (!compare(other, value)) {
                for (T x : expected) {
                    count += !compare(x, value) && !compare(other, x);
                }
            }
            Check(s.count_range(value, other) == count, "Range count differs");
        }
    }

}


template<typename Set, typename Model>
void RandomTest(unsigned seed) {

    mt19937 rng(seed);
    Set s;
    Model model;
    Set other;
    Model otherModel;
    for (int step = 0; step < 12000; step++) {
        operations++;
        int value = (int)(rng() % 51) - 25;
        int operation = rng() % 16;
        if (operation <= 4) {
            s.insert(value);
            model.insert(value);
        }
        else if (operation == 5) {
            bool found = model.find(value) != model.end();
            Check(s.erase_one(value) == found, "Erase one differs");
            if (found) {
                model.erase(model.find(value));
            }
        }
        else if (operation == 6) {
            Check(s.erase(value) == model.erase(value), "Erase key differs");
        }
        else if (operation == 7) {
            size_t idx = rng() % (model.size() + 3);
            bool found = idx < model.size();
            Check(s.erase_by_order(idx) == found, "Erase by order differs");
            if (found) {
                model.erase(next(model.begin(), idx));
            }
        }
        else if (operation == 8) {
            size_t first = rng() % (model.size() + 1);
            size_t last = rng() % (model.size() + 1);
            if (first > last) {
                swap(first, last);
            }
            auto expected = model.erase(next(model.begin(), first), next(model.begin(), last));
            auto result = s.erase(s.find_by_order(first), s.find_by_order(last));
            Check((result == s.end()) == (expected == model.end()), "Erase range end differs");
            if (expected != model.end()) {
                Check(*result == *expected, "Erase range successor differs");
            }
        }
        else if (operation == 9) {
            if (rng() % 31 == 0) {
                s.clear();
                model.clear();
            }
        }
        else if (operation == 10) {
            Set copy(s);
            Validate(copy, model);
            copy.insert(100);
            Check(!s.contains(100), "Copy shares storage");
            copy = s;
            Check(copy.size() == s.size(), "Copy assignment differs");
            Set* copyAddress = addressof(copy);
            copy = *copyAddress;
            Check(copy.size() == s.size(), "Self-copy differs");
        }
        else if (operation == 11) {
            Set moved(std::move(s));
            Check(s.empty(), "Moved-from object is not empty");
            s.insert(500);
            s = std::move(moved);
            Check(moved.empty(), "Move assignment did not empty source");
            Set* address = addressof(s);
            s = std::move(*address);
            Check(s.size() == model.size(), "Self-move differs");
        }
        else if (operation == 12) {
            other.insert(value);
            otherModel.insert(value);
            swap(s, other);
            model.swap(otherModel);
        }
        else if (operation == 13) {
            Validate(s, model);
        }
        else if (operation == 14) {
            vector<int> values = {value, value + 1, value};
            s.insert(values.begin(), values.end());
            model.insert(values.begin(), values.end());
        }
        else if (!s.empty()) {
            int first = *model.begin();
            size_t expected = model.erase(first);
            Check(s.erase(*s.begin()) == expected, "Aliased erase key differs");
        }
        Check(s.size() == model.size(), "Mutation size differs");
        if (step % 41 == 0) {
            Validate(s, model);
            Validate(other, otherModel);
        }
    }
    Validate(s, model);
    Validate(other, otherModel);

}


template<typename Set>
void EmptyTest() {

    Set s;
    Check(s.empty() && s.size() == 0, "Initial state differs");
    Check(s.begin() == s.end(), "Empty iterators differ");
    Check(s.erase(s.end()) == s.end(), "Erasing end differs");
    Check(s.erase(3) == 0 && !s.erase_one(3), "Missing erase differs");
    Check(!s.erase_by_order(0), "Empty erase by order differs");
    Check(s.first_index(3) == -1 && s.last_index(3) == -1, "Missing indices differ");
    CheckOutOfRange([&]() { (void)s[0]; });
    CheckOutOfRange([&]() { (void)s.at(numeric_limits<size_t>::max()); });
    CheckOutOfRange([&]() { (void)s.front(); });
    CheckOutOfRange([&]() { (void)s.back(); });
    s.insert(5);
    CheckOutOfRange([&]() { (void)s[1]; });
    Check(s.erase_by_order(0) && s.empty(), "Erase final element differs");
    s.clear();
    s.insert(7);
    Check(s.front() == 7 && s.back() == 7, "Reuse after clear differs");

}


template<typename Set, typename Model>
void ExhaustiveTest(const Set& s, const Model& model, int remaining) {

    exhaustiveStates++;
    vector<int> expected(model.begin(), model.end());
    Check(vector<int>(s.begin(), s.end()) == expected, "Exhaustive contents differ");
    Check(s.size() == expected.size(), "Exhaustive size differs");
    for (size_t i = 0; i < expected.size(); i++) {
        Check(s[i] == expected[i], "Exhaustive select differs");
    }
    for (int value : {-1, 0, 1}) {
        Check(s.order_of_key(value) == (size_t)distance(model.begin(), model.lower_bound(value)), "Exhaustive rank differs");
        Check(s.count(value) == model.count(value), "Exhaustive count differs");
    }
    if (!remaining) {
        return;
    }
    for (int value : {-1, 0, 1}) {
        for (int operation = 0; operation < 3; operation++) {
            Set current(s);
            Model currentModel(model);
            if (operation == 0) {
                current.insert(value);
                currentModel.insert(value);
            }
            else if (operation == 1) {
                auto it = currentModel.find(value);
                Check(current.erase_one(value) == (it != currentModel.end()), "Exhaustive erase one differs");
                if (it != currentModel.end()) {
                    currentModel.erase(it);
                }
            }
            else {
                Check(current.erase(value) == currentModel.erase(value), "Exhaustive erase all differs");
            }
            ExhaustiveTest(current, currentModel, remaining - 1);
        }
    }

}


struct Direction {

    bool descending;

    Direction() = delete;
    explicit Direction(bool valueDescending) : descending(valueDescending) {

    }

    bool operator()(int a, int b) const {

        return descending ? a > b : a < b;

    }

};


struct Record {

    int key;
    int id;

};


struct RecordCompare {

    bool operator()(const Record& a, const Record& b) const {

        return a.key < b.key;

    }

};


struct Tracked {

    int value;
    static int copies;

    explicit Tracked(int initialValue) : value(initialValue) {

    }

    Tracked(const Tracked& other) : value(other.value) {

        copies++;

    }

};

int Tracked::copies = 0;


struct TrackedCompare {

    bool operator()(const Tracked& a, const Tracked& b) const {

        return a.value < b.value;

    }

};


template<typename Set>
void StatefulTest() {

    Set a(Direction(0));
    Set b(Direction(1));
    for (int x : {1, 3, 2, 2}) {
        a.insert(x);
        b.insert(x);
    }
    Check(a.front() == 1 && b.front() == 3, "Stateful comparator differs");
    auto saved = a.begin();
    swap(a, b);
    Check(a.front() == 3 && b.front() == 1, "Swap lost comparator");
    Check(*saved == 1 && b.index_of(saved) == 0, "Swap invalidated element iterator");
    Set copy(a);
    Check(copy.key_comp().descending && copy.front() == 3, "Copy lost comparator");
    Set moved(std::move(copy));
    Check(copy.empty() && moved.front() == 3, "Move lost comparator");
    b = moved;
    Check(b.front() == 3 && b.key_comp().descending, "Assignment lost comparator");
    a = std::move(b);
    Check(b.empty() && a.front() == 3, "Move assignment lost comparator");

}


void GenericTest() {

    ordered_multiset<ll> extremes = {LLONG_MIN, LLONG_MAX, 0, LLONG_MIN, LLONG_MAX};
    Check(extremes.count(LLONG_MIN) == 2 && extremes.count(LLONG_MAX) == 2, "Extreme count differs");
    Check(extremes.order_of_key(LLONG_MIN) == 0, "Minimum rank differs");
    Check(extremes.order_of_key_upper(LLONG_MAX) == 5, "Maximum rank differs");
    Check(extremes.count_range(LLONG_MIN, LLONG_MAX) == 5, "Extreme range differs");
    Check(extremes.erase(LLONG_MAX) == 2, "Maximum erase differs");
    ordered_set<unsigned long long> unsignedValues = {0, ULLONG_MAX};
    Check(unsignedValues.order_of_key_upper(ULLONG_MAX) == 2, "Unsigned maximum differs");

    ordered_multiset<string> names = {"", "Ali", "Tareq", "Ali"};
    Check(names[0].empty() && names[1] == "Ali", "String order differs");
    Check(names.count("Ali") == 2 && names.first_index("Ali") == 1, "String ranks differ");
    Check(names.begin()->empty(), "Iterator arrow differs");
    Check(names.erase(*names.find("Ali")) == 2, "Aliased string erase differs");
    ordered_set<pair<int, string>> pairs = {{1, "b"}, {1, "a"}, {0, "z"}};
    Check(pairs[1] == make_pair(1, string("a")), "Pair order differs");
    Check(pairs.emplace(3, "c").second, "Unique emplace differs");
    pairs.insert({{4, "x"}, {4, "x"}});
    Check(pairs.count({4, "x"}) == 1, "Unique initializer insertion differs");
    names.emplace(3, 'z');
    names.insert({"new", "new"});
    Check(names.count("zzz") == 1 && names.count("new") == 2, "Multi emplace or initializer insertion differs");

    ordered_multiset<Record, RecordCompare> records;
    records.insert({5, 1});
    records.insert({2, 2});
    records.insert({5, 3});
    Check(records.count({5, 0}) == 2, "Comparator equivalence differs");
    Check(records[1].id == 1 && records[2].id == 3, "Equivalent-key insertion order differs");
    Check(records.erase({5, 99}) == 2, "Equivalent-key erase differs");
    ordered_set<Record, RecordCompare> uniqueRecords;
    Check(uniqueRecords.insert({4, 1}).second, "Record insertion differs");
    Check(!uniqueRecords.insert({4, 2}).second && uniqueRecords[0].id == 1, "Equivalent unique insertion differs");

    ordered_multiset<Tracked, TrackedCompare> tracked;
    tracked.insert(Tracked(3));
    tracked.insert(Tracked(3));
    tracked.insert(Tracked(8));
    Tracked probe(3);
    Tracked::copies = 0;
    Check(tracked.count(probe) == 2, "Tracked count differs");
    Check(tracked.contains(probe), "Tracked contains differs");
    Check(tracked.lower_bound(probe)->value == 3, "Tracked lower bound differs");
    Check(tracked.upper_bound(probe)->value == 8, "Tracked upper bound differs");
    Check(tracked.first_index(probe) == 0 && tracked.last_index(probe) == 1, "Tracked indices differ");
    Check(Tracked::copies == 0, "Lookup copied the key");

    StatefulTest<OrderedSet<int, Direction>>();
    StatefulTest<OrderedMultiSet<int, Direction>>();

}


void IteratorTest() {

    ordered_multiset<int> s = {2, 2, 2, 9};
    auto first = s.find_by_order(0);
    auto middle = s.find_by_order(1);
    auto last = s.find_by_order(2);
    const int* address = addressof(*middle);
    s.insert(2);
    s.insert(1);
    Check(*middle == 2 && addressof(*middle) == address, "Insertion invalidated iterator");
    s.erase(first);
    Check(*middle == 2 && s.index_of(middle) == 1, "Erase invalidated another duplicate");
    auto next = s.erase(middle);
    Check(next == last && *last == 2, "Iterator erase returned wrong occurrence");
    Check(addressof(*s.begin()) != addressof(*last), "Iterator identity differs");
    auto copied = s;
    copied.insert(2);
    s.insert(2);
    Check(copied.count(2) == s.count(2), "Copy duplicated insertion IDs");
    ordered_multiset<int> other = {2, 3};
    swap(s, other);
    s.insert(2);
    other.insert(2);
    Check(s.count(2) == 2 && other.count(2) == 4, "Swap lost insertion IDs");

    ordered_multiset<int> fromList = {1, 1, 3};
    vector<int> source = {5, 5, 7};
    ordered_multiset<int> fromRange(source.begin(), source.end());
    Check(fromList.count(1) == 2 && fromRange.count(5) == 2, "Construction differs");
    ordered_multiset<int> assigned;
    assigned = {4, 4, 8};
    Check(assigned.count(4) == 2, "Initializer-list assignment differs");

}


void OverflowTest() {

    using Small = ordered_multiset<int, less<int>, uint8_t>;
    Small s;
    for (int i = 0; i < 255; i++) {
        s.insert(i % 3);
    }
    bool caught = 0;
    try {
        s.insert(1);
    }
    catch (const length_error&) {
        caught = 1;
    }
    Check(caught && s.size() == 255 && s.count(0) == 85, "ID exhaustion corrupted the tree");
    Small copy(s);
    copy.clear();
    copy.insert(9);
    Check(copy.size() == 1 && s.size() == 255, "Clear or copy lost ID state");
    Small moved(std::move(copy));
    copy.insert(1);
    Check(copy.size() == 1 && moved.size() == 1, "Moved-from ID state differs");
    Small small;
    small.insert(3);
    swap(small, s);
    s.insert(3);
    Check(s.count(3) == 2 && small.size() == 255, "Swapped ID state differs");

}


void LargeTest() {

    const int n = 200000;
    ordered_set<int> s;
    ordered_multiset<int> ms;
    for (int i = 0; i < n; i++) {
        s.insert(i);
        ms.insert(i / 2);
    }
    for (int i = 0; i < n; i += 3) {
        Check(s[i] == i && s.order_of_key(i) == (size_t)i, "Large unique ranks differ");
        Check(ms[i] == i / 2, "Large duplicate ranks differ");
        Check(ms.count(i / 2) == 2, "Large duplicate counts differ");
    }
    for (int i = 0; i < n; i++) {
        Check(s.erase_one(i), "Large unique erase differs");
    }
    for (int i = 0; i < n / 2; i++) {
        Check(ms.erase(i) == 2, "Large duplicate erase differs");
    }
    Check(s.empty() && ms.empty(), "Large trees did not empty");

}


int main() {

    ios_base :: sync_with_stdio(0);
    cin.tie(0);
    cout.tie(0);

    using Raw = __gnu_pbds::tree<int, __gnu_pbds::null_type, less<int>,
                               __gnu_pbds::rb_tree_tag,
                               __gnu_pbds::tree_order_statistics_node_update>;
    static_assert(sizeof(ordered_set<int>) == sizeof(Raw));
    static_assert(sizeof(ordered_set<int>::iterator) == sizeof(void*));
    static_assert(sizeof(ordered_multiset<int>::iterator) == sizeof(void*));
    static_assert(is_same_v<decltype(declval<ordered_set<int>&>()[0]), const int&>);
    static_assert(is_same_v<decltype(declval<ordered_multiset<int>&>()[0]), const int&>);
    static_assert(!is_assignable_v<decltype(declval<ordered_multiset<int>&>()[0]), int>);

    try {
        EmptyTest<ordered_set<int>>();
        EmptyTest<ordered_multiset<int>>();
        GenericTest();
        IteratorTest();
        OverflowTest();
        ExhaustiveTest(ordered_set<int>(), set<int>(), 5);
        ExhaustiveTest(ordered_multiset<int>(), multiset<int>(), 5);
        ExhaustiveTest(ordered_set<int, greater<int>>(), set<int, greater<int>>(), 5);
        ExhaustiveTest(ordered_multiset<int, greater<int>>(), multiset<int, greater<int>>(), 5);
        for (unsigned seed = 1; seed <= 8; seed++) {
            RandomTest<ordered_set<int>, set<int>>(seed);
            RandomTest<ordered_multiset<int>, multiset<int>>(seed);
            RandomTest<ordered_set<int, greater<int>>, set<int, greater<int>>>(seed);
            RandomTest<ordered_multiset<int, greater<int>>, multiset<int, greater<int>>>(seed);
        }
        LargeTest();
        cout << "Passed " << operations << " randomized operations, " << exhaustiveStates;
        cout << " exhaustive trace states, and " << checks << " checks." << endl;
    }
    catch (const exception& error) {
        cerr << "FAILED: " << error.what() << endl;
        return 1;
    }

    return 0;

}
