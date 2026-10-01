#include "mirror_merge.hpp"
#include <utility>

SortResult mirror_merge_sort(std::vector<int> arr) {
    SortResult res;
    res.data = std::move(arr);
    mirror_merge_detail::sort(res.data, res.comparisons, res.moves, true);
    return res;
}

SortResult mirror_merge_sort_basic(std::vector<int> arr) {
    SortResult res;
    res.data = std::move(arr);
    mirror_merge_detail::sort(res.data, res.comparisons, res.moves, false);
    return res;
}
