# Examples

Include `OrderedSet.hpp` first. Body snippets go inside a function; recipe function definitions go above `main`. All indices are zero-based.

## QuickStart

<!-- example: QuickStart -->
```cpp
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

## RawPBDS

<!-- example: RawPBDS -->
```cpp
using RawOrderedSet = __gnu_pbds::tree<int, __gnu_pbds::null_type,
                                     less<int>, __gnu_pbds::rb_tree_tag,
                                     __gnu_pbds::tree_order_statistics_node_update>;

RawOrderedSet s;
s.insert(2);
s.insert(5);
s.insert(7);

cout << s.order_of_key(6) << '\n';                  // 2
cout << *s.find_by_order(1) << '\n';                // 5
```

## Construction

<!-- example: Construction -->
```cpp
ordered_set<int> a;
ordered_set<long long> b = {9, 2, 9};
ordered_multiset<string> names = {"Ali", "Tareq", "Ali"};
ordered_set<pair<int, int>> pairs = {{2, 3}, {1, 4}};

vector<int> v = {8, 3, 8, 1};
ordered_multiset<int> fromVector(v.begin(), v.end());
ordered_set<int> uniqueValues(v.begin(), v.end());

cout << b.size() << '\n';                           // 2
cout << names.count("Ali") << '\n';                 // 2
cout << pairs[0].second << '\n';                    // 4
cout << fromVector[2] << '\n';                      // 8
cout << uniqueValues.size() << '\n';                // 3
cout << a.empty() << '\n';                          // 1
```

## Descending

<!-- example: Descending -->
```cpp
ordered_multiset<int, greater<int>> s = {2, 9, 4, 9};

cout << s[0] << '\n';                               // 9
cout << s.order_of_key(4) << '\n';                  // 2: values before 4 are 9, 9
cout << *s.lower_bound(5) << '\n';                  // 4
cout << s.count_range(9, 3) << '\n';                // 3: 9, 9, 4
cout << s.count_range(3, 9) << '\n';                // 0: reversed in this ordering
```

## CustomKeys

<!-- example: CustomKeys -->
```cpp
struct Player {

    string name;
    int score;

};

struct ComparePlayer {

    bool operator()(const Player& a, const Player& b) const {

        return a.score > b.score;

    }

};

ordered_multiset<Player, ComparePlayer> players;
players.insert({"Ali", 100});
players.insert({"Tareq", 100});
players.insert({"Omar", 80});

cout << players[0].name << '\n';                    // Ali
cout << players[1].name << '\n';                    // Tareq
cout << players.count({"Anyone", 100}) << '\n';     // 2
cout << players.begin()->score << '\n';             // 100
```

## Inversions

<!-- example: Inversions -->
```cpp
long long CountInversions(const vector<int>& v) {

    ordered_multiset<int> s;
    long long ans = 0;
    for (int value : v) {
        ans += s.size() - s.order_of_key_upper(value);
        s.insert(value);
    }
    return ans;

}
```

## SlidingMedian

<!-- example: SlidingMedian -->
```cpp
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

## NarrowId

<!-- example: NarrowId -->
```cpp
ordered_multiset<int, less<int>, uint32_t> s;
s.insert(5);
cout << s[0] << '\n';                               // 5
```

