import unittest

from merge_sort_tree import MergeSortTree


class TestConstruction(unittest.TestCase):
    """The constructor must accept anything ``list()`` accepts and must
    not retain a reference to a mutable input."""

    def test_accepts_list(self):
        tree = MergeSortTree([5, 3, 8, 3, 1])
        self.assertEqual(len(tree), 5)

    def test_accepts_tuple(self):
        tree = MergeSortTree((5, 3, 8, 3, 1))
        self.assertEqual(len(tree), 5)

    def test_accepts_generator(self):
        tree = MergeSortTree(x for x in [5, 3, 8, 3, 1])
        self.assertEqual(len(tree), 5)

    def test_accepts_empty(self):
        tree = MergeSortTree([])
        self.assertEqual(len(tree), 0)

    def test_accepts_single_element(self):
        tree = MergeSortTree([42])
        self.assertEqual(len(tree), 1)

    def test_input_mutation_does_not_affect_tree(self):
        data = [5, 3, 8, 1]
        tree = MergeSortTree(data)
        data[0] = 999
        data.append(1000)
        self.assertEqual(tree.count_less(0, 4, 10), 4)


class TestCountLess(unittest.TestCase):
    """Behavioural contract for ``count_less``.

    The method counts elements strictly less than ``x`` in the
    half-open range ``[left, right)``.
    """

    def setUp(self):
        # Fixed, deterministic input. The tree is rebuilt per test for
        # isolation; construction is cheap at this size.
        self.arr = [5, 3, 8, 3, 1, 9, 2, 7]
        self.tree = MergeSortTree(self.arr)

    def test_full_range_below_max(self):
        # Every element is < 10.
        self.assertEqual(self.tree.count_less(0, 8, 10), 8)

    def test_full_range_above_max(self):
        # No element is < 0.
        self.assertEqual(self.tree.count_less(0, 8, 0), 0)

    def test_full_range_at_existing_value(self):
        # Values strictly less than 5: 3, 3, 1, 2 -> 4.
        self.assertEqual(self.tree.count_less(0, 8, 5), 4)

    def test_subrange_single_element(self):
        # arr[3] == 3, which is not < 3.
        self.assertEqual(self.tree.count_less(3, 4, 3), 0)
        self.assertEqual(self.tree.count_less(3, 4, 4), 1)

    def test_subrange_two_elements(self):
        # arr[2:4] = [8, 3]; < 5 -> just 3.
        self.assertEqual(self.tree.count_less(2, 4, 5), 1)

    def test_empty_query_range(self):
        # left == right is a zero-length slice.
        self.assertEqual(self.tree.count_less(3, 3, 5), 0)

    def test_query_at_boundaries(self):
        self.assertEqual(self.tree.count_less(0, 1, 6), 1)
        self.assertEqual(self.tree.count_less(7, 8, 8), 1)

    def test_query_value_between_elements(self):
        # No element equals 4, but 3, 3, 1, 2 are < 4.
        self.assertEqual(self.tree.count_less(0, 8, 4), 4)

    def test_query_value_equal_to_min(self):
        # Nothing is < 1.
        self.assertEqual(self.tree.count_less(0, 8, 1), 0)

    def test_query_value_equal_to_max(self):
        # Everything except 9 is < 9 -> 7.
        self.assertEqual(self.tree.count_less(0, 8, 9), 7)

    def test_repeated_values(self):
        # arr has two 3s. < 3 counts 1 and 2 -> 2.
        self.assertEqual(self.tree.count_less(0, 8, 3), 2)

    def test_negative_numbers(self):
        tree = MergeSortTree([-5, -3, -8, -3, -1])
        self.assertEqual(tree.count_less(0, 5, -3), 2)
        self.assertEqual(tree.count_less(0, 5, 0), 5)

    def test_strings(self):
        tree = MergeSortTree(["banana", "apple", "cherry", "apple"])
        self.assertEqual(tree.count_less(0, 4, "cherry"), 3)
        self.assertEqual(tree.count_less(0, 4, "apple"), 0)


class TestCountLessValidation(unittest.TestCase):
    """``count_less`` must reject out-of-range indices."""

    def setUp(self):
        self.tree = MergeSortTree([5, 3, 8, 3, 1])

    def test_left_negative(self):
        with self.assertRaises(IndexError):
            self.tree.count_less(-1, 3, 5)

    def test_right_too_large(self):
        with self.assertRaises(IndexError):
            self.tree.count_less(0, 6, 5)

    def test_left_greater_than_right(self):
        with self.assertRaises(IndexError):
            self.tree.count_less(3, 1, 5)


class TestEmptyTree(unittest.TestCase):
    """An empty tree must answer every query with 0 without error."""

    def test_empty_query_on_empty_tree(self):
        tree = MergeSortTree([])
        self.assertEqual(tree.count_less(0, 0, 5), 0)

    def test_empty_tree_rejects_bad_indices(self):
        tree = MergeSortTree([])
        with self.assertRaises(IndexError):
            tree.count_less(0, 1, 5)


if __name__ == "__main__":
    unittest.main()
