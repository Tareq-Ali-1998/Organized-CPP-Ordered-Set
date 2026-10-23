
long long recipeChecks = 0;

void Check(bool ok, const char* message) {

    if (!ok) {
        throw runtime_error(message);
    }

}

void CheckRecipes(const vector<int>& v) {

    long long inversions = 0;
    for (size_t i = 0; i < v.size(); i++) {
        for (size_t j = i + 1; j < v.size(); j++) {
            inversions += v[i] > v[j];
        }
    }
    Check(CountInversions(v) == inversions, "Inversion recipe differs");
    recipeChecks++;

    for (int k = 1; (size_t)k <= v.size(); k++) {
        vector<int> expected;
        for (size_t first = 0; first + k <= v.size(); first++) {
            vector<int> window(v.begin() + first, v.begin() + first + k);
            sort(window.begin(), window.end());
            expected.push_back(window[(k - 1) / 2]);
        }
        Check(SlidingMedian(v, k) == expected, "Median recipe differs");
        recipeChecks++;
    }

    for (int k : {-1, 0, (int)v.size() + 1}) {
        bool caught = 0;
        try {
            SlidingMedian(v, k);
        }
        catch (const invalid_argument&) {
            caught = 1;
        }
        Check(caught, "Invalid window size was accepted");
        recipeChecks++;
    }

}

void ExhaustiveRecipes() {

    int combinations = 1;
    for (int n = 0; n <= 7; n++) {
        for (int mask = 0; mask < combinations; mask++) {
            vector<int> v(n);
            int current = mask;
            for (int i = 0; i < n; i++) {
                v[i] = current % 3 - 1;
                current /= 3;
            }
            CheckRecipes(v);
        }
        combinations *= 3;
    }
    CheckRecipes({3, 1, 2, 2});
    CheckRecipes({5, 1, 5, 2, 9, 2});
    CheckRecipes({INT_MAX, INT_MIN, INT_MAX, INT_MIN, 0});
    CheckRecipes(vector<int>(20, 7));

}
