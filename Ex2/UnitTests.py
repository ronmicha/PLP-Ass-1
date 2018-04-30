import unittest
from Ex2 import ComplexNum, isInstancePPL


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
    def setUp(self):
        class C0:
            pass

        class C1_0(C0):
            pass

        class C2_0(C0):
            pass

        class C3_12(C1_0, C2_0):
            pass

        class C4_2(C2_0):
            pass

        class C5_1(C1_0):
            pass

        class Cobj_obj(object):
            pass

        class Cobj2_Cojb(Cobj_obj):
            pass

        self.C0 = C0
        self.C1_0 = C1_0
        self.C2_0 = C2_0
        self.C3_12 = C3_12
        self.C4_2 = C4_2
        self.C5_1 = C5_1
        self.Cobj_obj = Cobj_obj
        self.Cobj2_Cojb = Cobj2_Cojb

    def test_isinstance_objects(self):
        self.assertTrue(isInstancePPL(self.C0(), self.C0))
        self.assertTrue(isInstancePPL(self.C1_0(), self.C0))
        self.assertTrue(isInstancePPL(self.C2_0(), self.C0))
        self.assertTrue(isInstancePPL(self.C1_0(), self.C1_0))
        self.assertTrue(isInstancePPL(self.C2_0(), self.C2_0))

        self.assertTrue(isInstancePPL(self.C3_12(), self.C0))
        self.assertTrue(isInstancePPL(self.C3_12(), self.C1_0))
        self.assertTrue(isInstancePPL(self.C3_12(), self.C2_0))
        self.assertFalse(isInstancePPL(self.C3_12(), self.C4_2))

        self.assertFalse(isInstancePPL(self.C4_2(), self.C1_0))
        self.assertTrue(isInstancePPL(self.C3_12(), self.C0))

        self.assertFalse(isInstancePPL(self.C5_1(), self.C3_12))

        self.assertTrue(isInstancePPL(self.Cobj_obj(), object))
        self.assertTrue(isInstancePPL(self.Cobj2_Cojb(), object))
        self.assertTrue(isInstancePPL(self.Cobj2_Cojb(), self.Cobj_obj))
        self.assertFalse(isInstancePPL(self.C0(), object))
        self.assertFalse(isInstancePPL(self.C5_1(), object))

    def test_isinstance_variables(self):
        with self.assertRaises(TypeError):
            isInstancePPL(None, int)
        with self.assertRaises(TypeError):
            isInstancePPL(1, None)

        self.assertTrue(isInstancePPL(1, int))
        # self.assertTrue(isInstancePPL(1, float))
        # self.assertTrue(isInstancePPL(1.0, int))
        self.assertTrue(isInstancePPL(1.0, float))
        self.assertTrue(isInstancePPL(1.5, float))
        self.assertTrue(isInstancePPL("test", str))
        # self.assertTrue(isInstancePPL(lambda x: 2 * x, function))
        self.assertTrue(isInstancePPL([1, 'a'], list))
        self.assertTrue(isInstancePPL({"1": 1, "2": "2"}, dict))
        self.assertTrue(isInstancePPL(set(), set))
        self.assertTrue(isInstancePPL((1, 2), tuple))


if __name__ == '__main__':
    unittest.main()
