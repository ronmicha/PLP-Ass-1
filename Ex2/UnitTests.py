import unittest
from ComplexNum import ComplexNum


class TestComplexNum(unittest.TestCase):
    def initTest(self):
        with self.assertRaises(TypeError):
            ComplexNum("fa", "fb")

if __name__ == '__main__':
    unittest.main()
