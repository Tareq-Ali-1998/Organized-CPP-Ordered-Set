#include "OrderedSet.hpp"

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
