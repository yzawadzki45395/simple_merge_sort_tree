# merge-sort-tree

A merge sort tree for Python: preprocess an array in `O(n log n)` time and
then answer "how many values in `arr[l:r]` are strictly less than `x`?" in
`O(log^2 n)` time per query.

## Usage

```python
from merge_sort_tree import MergeSortTree

tree = MergeSortTree([5, 3, 8, 3, 1, 9, 2, 7])

# Count elements in arr[0:8] that are strictly less than 5.
assert tree.count_less(0, 8, 5) == 4

# Half-open ranges, so this looks at arr[2:4] = [8, 3].
assert tree.count_less(2, 4, 5) == 1

# Empty query range is always zero.
assert tree.count_less(3, 3, 5) == 0
```

The only exported name is `MergeSortTree`. Its constructor takes any
sequence (list, tuple, generator) of mutually comparable values and copies
them internally, so mutating the original input after construction has no
effect on the tree. The single query method is

```python
tree.count_less(left: int, right: int, x) -> int
```

where `[left, right)` is a half-open interval into the original sequence and
the result is the number of elements in that slice strictly less than `x`.

## Why this exists

Range counting shows up in offline query problems, order statistics over
subarrays, and as a building block for two-dimensional counting. A merge
sort tree is the simplest structure that answers these queries without the
implementation weight of a wavelet tree or a persistent segment tree.

The trade-off is memory: every element lives in `O(log n)` sorted node
arrays, so total memory is `O(n log n)`. For `n` up to a few hundred
thousand this is fine in Python; beyond that, consider a wavelet tree.

## Deriving other comparisons

Only `count_less` is provided. Other relations follow on the caller's side:

- `count_less_equal(l, r, x)` = `count_less(l, r, x) + count_equal(l, r, x)`
- `count_greater(l, r, x)` = `(r - l) - count_less_equal(l, r, x)`
- `count_equal(l, r, x)` = `count_less(l, r, x+1) - count_less(l, r, x)`
  (works for integers; for floats use the next representable value)

## Edge cases worth knowing

- `count_less` raises `IndexError` unless `0 <= left <= right <= n`. The
  half-open convention means `left == right` is a valid zero-length query
  and returns `0`.
- An empty tree (`MergeSortTree([])`) is legal; `count_less(0, 0, x)`
  returns `0`.
- The comparison value `x` does not need to be the same type as the stored
  values, only comparable to them. Comparing incompatible types raises
  `TypeError` from the underlying comparison, which is allowed to propagate.
