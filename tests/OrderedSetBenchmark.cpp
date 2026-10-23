#include <bits/stdc++.h>
#include "../OrderedSet.hpp"

using namespace std;

#define endl '\n'
#define ll long long
#define LSB __builtin_ctzll
#define MSB 63-__builtin_clzll
#define BITS __builtin_popcountll


using Clock = chrono::steady_clock;


double Seconds(Clock::time_point first, Clock::time_point last) {

    return chrono::duration<double>(last - first).count();

}


template<typename Tree, bool RawMulti, bool Wrapped>
void Run(const string& name, int n, const vector<int>& values, const vector<unsigned>& indices) {

    Tree s;
    auto start = Clock::now();
    for (int i = 0; i < n; i++) {
        if constexpr (RawMulti) {
            using Entry = typename Tree::key_type;
            s.insert(Entry(values[i], i));
        }
        else {
            s.insert(values[i]);
        }
    }
    auto inserted = Clock::now();

    unsigned long long checksum = 0;
    for (int i = 0; i < n; i++) {
        if constexpr (RawMulti) {
            using Entry = typename Tree::key_type;
            checksum += s.order_of_key(Entry(values[i], 0));
            checksum += s.find_by_order(indices[i] % s.size())->first;
        }
        else {
            checksum += s.order_of_key(values[i]);
            if constexpr (Wrapped) {
                checksum += s[indices[i] % s.size()];
            }
            else {
                checksum += *s.find_by_order(indices[i] % s.size());
            }
        }
    }
    auto queried = Clock::now();

    for (int i = 0; i < n / 2; i++) {
        if constexpr (RawMulti) {
            using Entry = typename Tree::key_type;
            auto it = s.lower_bound(Entry(values[i], 0));
            if (it != s.end() && it->first == values[i]) {
                s.erase(it);
            }
        }
        else if constexpr (Wrapped) {
            s.erase_one(values[i]);
        }
        else {
            s.erase(values[i]);
        }
    }
    auto erased = Clock::now();

    cout << fixed << setprecision(6);
    cout << "{\"mode\":\"" << name << "\",\"n\":" << n;
    cout << ",\"object_bytes\":" << sizeof(Tree);
    cout << ",\"insert_seconds\":" << Seconds(start, inserted);
    cout << ",\"query_seconds\":" << Seconds(inserted, queried);
    cout << ",\"erase_seconds\":" << Seconds(queried, erased);
    cout << ",\"total_seconds\":" << Seconds(start, erased);
    cout << ",\"remaining\":" << s.size() << ",\"checksum\":" << checksum << "}" << endl;

}


template<typename Id>
using RawMulti = __gnu_pbds::tree<pair<int, Id>, __gnu_pbds::null_type,
                                less<pair<int, Id>>, __gnu_pbds::rb_tree_tag,
                                __gnu_pbds::tree_order_statistics_node_update>;

using RawSet = __gnu_pbds::tree<int, __gnu_pbds::null_type, less<int>,
                              __gnu_pbds::rb_tree_tag,
                              __gnu_pbds::tree_order_statistics_node_update>;


int main(int argc, char** argv) {

    ios_base :: sync_with_stdio(0);
    cin.tie(0);
    cout.tie(0);

    string mode = argc > 1 ? argv[1] : "set";
    int n = argc > 2 ? stoi(argv[2]) : 200000;
    if (n < 1 || n > 10000000) {
        cerr << "Use a size between 1 and 10000000." << endl;
        return 1;
    }

    mt19937 rng(20261020);
    bool multi = mode.find("multi") != string::npos;
    int distinct = multi ? max(1, n / 100) : n * 2;
    vector<int> values(n);
    vector<unsigned> indices(n);
    for (int i = 0; i < n; i++) {
        values[i] = rng() % distinct;
        indices[i] = rng();
    }

    if (mode == "raw_set") {
        Run<RawSet, false, false>(mode, n, values, indices);
    }
    else if (mode == "set") {
        Run<ordered_set<int>, false, true>(mode, n, values, indices);
    }
    else if (mode == "raw_multi64") {
        Run<RawMulti<uint64_t>, true, false>(mode, n, values, indices);
    }
    else if (mode == "multi64") {
        Run<ordered_multiset<int>, false, true>(mode, n, values, indices);
    }
    else if (mode == "raw_multi32") {
        Run<RawMulti<uint32_t>, true, false>(mode, n, values, indices);
    }
    else if (mode == "multi32") {
        Run<ordered_multiset<int, less<int>, uint32_t>, false, true>(mode, n, values, indices);
    }
    else {
        cerr << "Modes: raw_set, set, raw_multi64, multi64, raw_multi32, multi32." << endl;
        return 1;
    }

    return 0;

}
