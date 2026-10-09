"""Merge Sort Tree for range-counting queries.

A merge sort tree stores, at each node of a segment tree, the sorted
subarray covering that node's interval. This lets us answer queries of
the form "how many values in ``arr[l:r]`` are strictly less than ``x``?"
in ``O(log^2 n)`` time after ``O(n log n)`` preprocessing.

Design decisions
----------------
* The tree stores *copies* of the input values, not indices. This keeps
  the query path free of indirect lookups and makes the structure safe to
  use even if the caller mutates the original array after construction.
  The cost is ``O(n log n)`` memory, which is the standard trade-off for
  this data structure.
* Only the ``count_less`` primitive is offered. Range-counting problems
  that need ``<=``, ``>``, ``>=``, or ``==`` can be derived from it by
  simple arithmetic on the caller's side (see README). Keeping the API
  to one primitive avoids the combinatorial explosion of methods that
  all delegate to the same binary search.
* The tree is built eagerly and never mutated afterwards. This is the
  common case for offline query workloads; supporting updates would
  turn an ``O(n log n)`` structure into something far heavier.
"""

from __future__ import annotations

from bisect import bisect_left
from typing import List, Sequence


class MergeSortTree:
    """Preprocess a sequence for range-counting queries.

    Once built, the tree answers in ``O(log^2 n)`` time the question:
    how many elements of ``arr[l:r]`` are strictly less than ``x``?

    Parameters
    ----------
    data:
        Any sequence of mutually comparable values. The values are copied
        during construction; later mutation of ``data`` does not affect
        the tree. ``len(data)`` may be zero.

    Attributes
    ----------
    n:
        Length of the input sequence.

    Notes
    -----
    Memory use is ``O(n log n)`` because every element appears in
    ``O(log n)`` node arrays. Construction time is ``O(n log n)``.
    """

    __slots__ = ("_n", "_tree")

    def __init__(self, data: Sequence[object]) -> None:
        # Materialise once: the caller may pass a generator or a view,
        # and we need random access during the recursive build.
        values: List[object] = list(data)
        n = len(values)
        self._n = n
        # A full binary segment tree on n leaves needs at most
        # 2 * 2**ceil(log2(n)) nodes; 4 * n is a safe upper bound that
        # also covers the n == 0 and n == 1 edge cases without special
        # casing. The extra slots stay empty lists, which is harmless.
        tree: List[List[object]] = [[] for _ in range(4 * n)] if n else []
        self._tree = tree
        if n:
            self._build(values, 1, 0, n - 1)

    # ------------------------------------------------------------------
    # construction
    # ------------------------------------------------------------------
    def _build(
        self,
        values: List[object],
        node: int,
        left: int,
        right: int,
    ) -> None:
        """Recursively build the subtree rooted at ``node``.

        ``left`` and ``right`` are inclusive indices into ``values``.
        Each node stores the sorted slice of ``values`` over its
        interval; merging two sorted children is linear, so the whole
        build is ``O(n log n)``.
        """
        if left == right:
            self._tree[node] = [values[left]]
            return
        mid = (left + right) // 2
        self._build(values, 2 * node, left, mid)
        self._build(values, 2 * node + 1, mid + 1, right)
        # ``list(...)`` of a generator would also work, but the explicit
        # loop avoids creating an intermediate iterator object per node.
        self._tree[node] = sorted(self._tree[2 * node] + self._tree[2 * node + 1])

    # ------------------------------------------------------------------
    # queries
    # ------------------------------------------------------------------
    def count_less(self, left: int, right: int, x: object) -> int:
        """Count elements in ``self[left:right]`` strictly less than ``x``.

        Parameters
        ----------
        left, right:
            Half-open interval ``[left, right)`` into the original
            sequence. Must satisfy ``0 <= left <= right <= n``.
        x:
            The comparison value. May be of any type comparable to the
            stored values; if it is not comparable, the resulting
            ``TypeError`` propagates to the caller.

        Returns
        -------
        int
            The number of indices ``i`` with ``left <= i < right`` and
            ``arr[i] < x``.

        Raises
        ------
        IndexError
            If ``left`` or ``right`` is out of bounds, or if
            ``left > right``.
        """
        n = self._n
        if not 0 <= left <= right <= n:
            raise IndexError(
                f"count_less requires 0 <= left <= right <= n (got "
                f"left={left}, right={right}, n={n})"
            )
        if left == right or n == 0:
            return 0
        return self._query(1, 0, n - 1, left, right - 1, x)

    def _query(
        self,
        node: int,
        node_left: int,
        node_right: int,
        q_left: int,
        q_right: int,
        x: object,
    ) -> int:
        """Count values < ``x`` in the intersection of ``[node_left,
        node_right]`` and ``[q_left, q_right]`` (both inclusive)."""
        # No overlap between the node's interval and the query.
        if q_left > node_right or q_right < node_left:
            return 0
        # Node fully inside the query: a single binary search over the
        # node's sorted array answers the count for its whole interval.
        if q_left <= node_left and node_right <= q_right:
            return bisect_left(self._tree[node], x)
        mid = (node_left + node_right) // 2
        return self._query(2 * node, node_left, mid, q_left, q_right, x) + self._query(
            2 * node + 1, mid + 1, node_right, q_left, q_right, x
        )

    # ------------------------------------------------------------------
    # dunder helpers
    # ------------------------------------------------------------------
    def __len__(self) -> int:
        """Return the length of the original input sequence."""
        return self._n
