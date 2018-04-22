import unittest

from pypict import api


class TestAPI(unittest.TestCase):
    def test_usecase_simple(self):
        task = api.Task()
        p1 = task.model.add_parameter(2, 2, [1, 1])
        p2 = task.model.add_parameter(3, 2, [2, 1, 1])
        self.assertEqual(2, task.get_total_parameter_count())
        task.add_exclusion([(p1, 0), (p2, 2)])
        task.add_exclusion([(p1, 1), (p2, 0)])
        task.add_seed([(p1, 0), (p2, 0)])
        patterns = sorted(list(task.generate()))
        self.assertEqual([[0, 0], [0, 1], [1, 1], [1, 2]], patterns)
