import unittest
import main

class UnitTests(unittest.TestCase):
    def test_distance_sort(self):
        self.assertEqual(main.sort_distance([{'distance':648, 'min_x': 45}, {'distance': 573, 'min_x': 16}, {'distance': 575, 'min_x': 15}]), [[{'distance':648, 'min_x': 45}], [{'distance': 575,'min_x': 15}, {'distance': 573, 'min_x': 16}]])
    def test_organize_for_speech(self):
        self.assertEqual(main.organize_for_speech([[{'name': 'chair','distance':648}], [{'name': 'person', 'distance': 575}, {'name': 'person', 'distance': 573}]]), 'In front of you there is a chair. Behind that is a person next to another person.')

if __name__ == "__main__":
    unittest.main()