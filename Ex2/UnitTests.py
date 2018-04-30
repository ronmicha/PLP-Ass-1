import unittest
from Ex2 import ComplexNum


class TestComplexNum(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(TypeError):
            ComplexNum("fa", "fb")
        with self.assertRaises(TypeError):
            ComplexNum(None, None)
        with self.assertRaises(TypeError):
            ComplexNum(None, 1)
        with self.assertRaises(TypeError):
            ComplexNum(1, None)
        with self.assertRaises(TypeError):
            ComplexNum(None, -1)
        with self.assertRaises(TypeError):
            ComplexNum(-1, None)

        x = ComplexNum(100, -56)
        self.assertEqual(x.re(), 100)
        self.assertEqual(x.im(), -56)

        y = ComplexNum(38.451, -987.12)
        self.assertEqual(y.re(), 38.451)
        self.assertEqual(y.im(), -987.12)

    def test_to_tuple(self):
        self.assertEqual(ComplexNum(15, -86).to_tuple(), (15, -86))
        self.assertEqual(ComplexNum(0, 0).to_tuple(), (0, 0))

    def test_repr(self):
        self.assertEqual(str(ComplexNum(1, 1)), "1 + 1i")
        self.assertEqual(str(ComplexNum(1, -1)), "1 - 1i")
        self.assertEqual(str(ComplexNum(1, 0)), "1")
        self.assertEqual(str(ComplexNum(1, 683.2)), "1 + 683.2i")
        self.assertEqual(str(ComplexNum(1, -357.68)), "1 - 357.68i")
        self.assertEqual(str(ComplexNum(1, -0)), "1")

        self.assertEqual(str(ComplexNum(-1, 1)), "-1 + 1i")
        self.assertEqual(str(ComplexNum(-1, -1)), "-1 - 1i")
        self.assertEqual(str(ComplexNum(-1, 0)), "-1")
        self.assertEqual(str(ComplexNum(-1, 135.2)), "-1 + 135.2i")
        self.assertEqual(str(ComplexNum(-1, -48.9)), "-1 - 48.9i")
        self.assertEqual(str(ComplexNum(-1, -0)), "-1")

        self.assertEqual(str(ComplexNum(0, 1)), "1i")
        self.assertEqual(str(ComplexNum(0, -1)), "-1i")
        self.assertEqual(str(ComplexNum(0, 0)), "0")
        self.assertEqual(str(ComplexNum(0, 135.2)), "135.2i")
        self.assertEqual(str(ComplexNum(0, -48.9)), "-48.9i")
        self.assertEqual(str(ComplexNum(0, -0)), "0")

    def test_equal(self):
        self.assertTrue(ComplexNum(1, 1) == ComplexNum(1, 1))
        self.assertTrue(ComplexNum(0, -0) == ComplexNum(0, 0))
        self.assertTrue(ComplexNum(-10, -0) == ComplexNum(-10, 0))
        self.assertFalse(ComplexNum(1, 1) == ComplexNum(2, 2))
        self.assertFalse(ComplexNum(-0, -0) == ComplexNum(-1, -1))

        with self.assertRaises(TypeError):
            ComplexNum(-1, 4) == 1
        with self.assertRaises(TypeError):
            ComplexNum(-1, 4) == "im a string"
        with self.assertRaises(TypeError):
            ComplexNum(-1, 4) == None


class TestInheritance(unittest.TestCase):
    class X:
        def __init__(self):
            self.message = 'X'

    class Y:
        def __init__(self):
            self.message = 'Y'

    pass


if __name__ == '__main__':
    unittest.main()
