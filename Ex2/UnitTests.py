import math
import unittest
from types import *
from Ex2 import *


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

    def test_add(self):
        sets = [
            [1, 2, 1, -3, 2, -1],
            [0, 0, 0, 0, 0, 0],
            [1, 2, 0, 0, 1, 2],
            [1, 2, -1, -2, 0, 0],
            [-1, -3, -2, -5, -3, -8],
            [3, 3, 0, 3, 3, 6],
            [4, 4, 4, 0, 8, 4]
        ]
        for numbers in sets:
            a1, b1, a2, b2, ra, rb = numbers
            # (a1+b1*i)+(a2+b2*i)=(ra+rb*i)
            self.assertTrue(ComplexNum(a1, b1) + ComplexNum(a2, b2) == ComplexNum(ra, rb))

    def test_subtract(self):
        sets = [
            [1, 2, 1, -3, 0, 5],
            [1, 2, 4, 3, -3, -1],
            [0, 0, 0, 0, 0, 0],
            [1, 2, 1, 2, 0, 0],
            [1, 2, 0, 0, 1, 2],
            [1, 2, -1, -2, 2, 4],
            [-1, -3, -2, -5, 1, 2],
            [3, 3, 0, 3, 3, 0],
            [4, 4, 4, 0, 0, 4]
        ]
        for numbers in sets:
            a1, b1, a2, b2, ra, rb = numbers
            self.assertTrue(ComplexNum(a1, b1) - ComplexNum(a2, b2) == ComplexNum(ra, rb))

    def test_multiply(self):
        sets = [
            [1, 2, 1, -3, 7, -1],
            [1, 2, 4, 3, -2, 11],
            [0, 0, 0, 0, 0, 0],
            [1, 2, 1, 2, -3, 4],
            [1, 2, 0, 0, 0, 0],
            [1, 2, -1, -2, 3, -4],
            [-1, -3, -2, -5, -13, 11],
            [3, 3, 0, 3, -9, 9],
            [4, 4, 4, 0, 16, 16]
        ]
        for numbers in sets:
            a1, b1, a2, b2, ra, rb = numbers
            # print ("(" + str(ComplexNum(a1, b1)) + ")*(" + str(ComplexNum(a2, b2)) + ")")
            self.assertTrue(ComplexNum(a1, b1) * ComplexNum(a2, b2) == ComplexNum(ra, rb))

    def test_conjugate(self):
        sets = [
            [1, 2],
            [1, 2],
            [0, 0],
            [1, 2],
            [-1, -3],
            [3, 3],
            [4, 4],
            [1, -1]
        ]
        for numbers in sets:
            a1, b1 = numbers
            # print ("(" + str(ComplexNum(a1, b1)) + ")*(" + str(ComplexNum(a2, b2)) + ")")
            self.assertTrue(ComplexNum(a1, b1).conjugate() == ComplexNum(a1, -b1))

    def test_abs(self):
        sets = [
            [1, 2],
            [0, 0],
            [1, 2],
            [-1, -3],
            [3, 3],
            [4, 4],
            [1, -1]
        ]
        for numbers in sets:
            a1, b1 = numbers
            self.assertTrue(ComplexNum(a1, b1).abs() == math.sqrt(a1 * a1 + b1 * b1))


class TestInheritance(unittest.TestCase):
    def setUp(self):
        class C0(object):
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
        self.assertTrue(isInstancePPL(self.C0(), object))
        self.assertTrue(isInstancePPL(self.C5_1(), object))

    def test_isinstance_variables(self):
        with self.assertRaises(TypeError):
            isInstancePPL(None, int)
        with self.assertRaises(TypeError):
            isInstancePPL(1, None)
        with self.assertRaises(TypeError):
            isInstancePPL(1, 1)
        with self.assertRaises(TypeError):
            isInstancePPL(1, "int")
        with self.assertRaises(TypeError):
            isInstancePPL(1, [int])

        self.assertTrue(isInstancePPL(1, int))
        self.assertFalse(isInstancePPL(1, float))
        self.assertFalse(isInstancePPL(1.0, int))
        self.assertTrue(isInstancePPL(1.0, float))
        self.assertTrue(isInstancePPL(1.5, float))
        self.assertTrue(isInstancePPL("test", str))
        self.assertTrue(isInstancePPL(lambda x: 2 * x, LambdaType))
        self.assertTrue(isInstancePPL(self.test_isinstance_objects, MethodType))
        self.assertTrue(isInstancePPL([1, 'a'], list))
        self.assertTrue(isInstancePPL({"1": 1, "2": "2"}, dict))
        self.assertTrue(isInstancePPL(set(), set))
        self.assertTrue(isInstancePPL((1, 2), tuple))

    def test_isinstance_objects_num(self):
        with self.assertRaises(TypeError):
            numInstancePPL(None, int)
        with self.assertRaises(TypeError):
            numInstancePPL(1, None)
        with self.assertRaises(TypeError):
            numInstancePPL(1, 1)
        with self.assertRaises(TypeError):
            numInstancePPL(1, "int")
        with self.assertRaises(TypeError):
            numInstancePPL(1, [int])

        self.assertEqual(numInstancePPL(self.C0(), self.C0), 1)
        self.assertEqual(numInstancePPL(self.C1_0(), self.C0), 2)
        self.assertEqual(numInstancePPL(self.C2_0(), self.C0), 2)
        self.assertEqual(numInstancePPL(self.C1_0(), self.C1_0), 1)
        self.assertEqual(numInstancePPL(self.C2_0(), self.C2_0), 1)
        self.assertEqual(numInstancePPL(self.C3_12(), self.C0), 3)
        self.assertEqual(numInstancePPL(self.C3_12(), self.C1_0), 2)
        self.assertEqual(numInstancePPL(self.C3_12(), self.C2_0), 2)
        self.assertEqual(numInstancePPL(self.C3_12(), self.C4_2), 0)
        self.assertEqual(numInstancePPL(self.C4_2(), self.C1_0), 0)
        self.assertEqual(numInstancePPL(self.C5_1(), self.C3_12), 0)
        self.assertEqual(numInstancePPL(self.Cobj_obj(), object), 2)
        self.assertEqual(numInstancePPL(self.Cobj2_Cojb(), object), 3)
        self.assertEqual(numInstancePPL(self.Cobj2_Cojb(), self.Cobj_obj), 2)
        self.assertEqual(numInstancePPL(self.C0(), object), 2)
        self.assertEqual(numInstancePPL(self.C5_1(), object), 4)

    def test_issubclass(self):
        with self.assertRaises(TypeError):
            isSubclassPPL(None, int)
        with self.assertRaises(TypeError):
            isSubclassPPL(int, None)
        with self.assertRaises(TypeError):
            isSubclassPPL(1, 1)
        with self.assertRaises(TypeError):
            isSubclassPPL(1, int)
        with self.assertRaises(TypeError):
            isSubclassPPL(int, [int])

        self.assertTrue(isSubclassPPL(self.C0, self.C0))
        self.assertTrue(isSubclassPPL(self.C1_0, self.C0))
        self.assertTrue(isSubclassPPL(self.C2_0, self.C0))
        self.assertTrue(isSubclassPPL(self.C1_0, self.C1_0))
        self.assertTrue(isSubclassPPL(self.C2_0, self.C2_0))
        self.assertTrue(isSubclassPPL(self.C3_12, self.C0))
        self.assertTrue(isSubclassPPL(self.C3_12, self.C1_0))
        self.assertTrue(isSubclassPPL(self.C3_12, self.C2_0))
        self.assertFalse(isSubclassPPL(self.C3_12, self.C4_2))
        self.assertFalse(isSubclassPPL(self.C4_2, self.C1_0))
        self.assertTrue(isSubclassPPL(self.C3_12, self.C0))
        self.assertFalse(isSubclassPPL(self.C5_1, self.C3_12))
        self.assertTrue(isSubclassPPL(self.Cobj_obj, object))
        self.assertTrue(isSubclassPPL(self.Cobj2_Cojb, object))
        self.assertTrue(isSubclassPPL(self.Cobj2_Cojb, self.Cobj_obj))
        self.assertTrue(isSubclassPPL(self.C0, object))
        self.assertTrue(isSubclassPPL(self.C5_1, object))

        self.assertTrue(isSubclassPPL(type(self.C0()), self.C0))
        self.assertTrue(isSubclassPPL(type(self.C1_0()), self.C0))
        self.assertTrue(isSubclassPPL(type(self.C2_0()), self.C0))
        self.assertTrue(isSubclassPPL(type(self.C1_0()), self.C1_0))
        self.assertTrue(isSubclassPPL(type(self.C2_0()), self.C2_0))
        self.assertTrue(isSubclassPPL(type(self.C3_12()), self.C0))
        self.assertTrue(isSubclassPPL(type(self.C3_12()), self.C1_0))
        self.assertTrue(isSubclassPPL(type(self.C3_12()), self.C2_0))
        self.assertFalse(isSubclassPPL(type(self.C3_12()), self.C4_2))
        self.assertFalse(isSubclassPPL(type(self.C4_2()), self.C1_0))
        self.assertTrue(isSubclassPPL(type(self.C3_12()), self.C0))
        self.assertFalse(isSubclassPPL(type(self.C5_1()), self.C3_12))
        self.assertTrue(isSubclassPPL(type(self.Cobj_obj()), object))
        self.assertTrue(isSubclassPPL(type(self.Cobj2_Cojb()), object))
        self.assertTrue(isSubclassPPL(type(self.Cobj2_Cojb()), self.Cobj_obj))
        self.assertTrue(isSubclassPPL(type(self.C0()), object))
        self.assertTrue(isSubclassPPL(type(self.C5_1()), object))

        self.assertTrue(isSubclassPPL(self.C0().__class__, self.C0))
        self.assertTrue(isSubclassPPL(self.C1_0().__class__, self.C0))
        self.assertTrue(isSubclassPPL(self.C2_0().__class__, self.C0))
        self.assertTrue(isSubclassPPL(self.C1_0().__class__, self.C1_0))
        self.assertTrue(isSubclassPPL(self.C2_0().__class__, self.C2_0))
        self.assertTrue(isSubclassPPL(self.C3_12().__class__, self.C0))
        self.assertTrue(isSubclassPPL(self.C3_12().__class__, self.C1_0))
        self.assertTrue(isSubclassPPL(self.C3_12().__class__, self.C2_0))
        self.assertFalse(isSubclassPPL(self.C3_12().__class__, self.C4_2))
        self.assertFalse(isSubclassPPL(self.C4_2().__class__, self.C1_0))
        self.assertTrue(isSubclassPPL(self.C3_12().__class__, self.C0))
        self.assertFalse(isSubclassPPL(self.C5_1().__class__, self.C3_12))
        self.assertTrue(isSubclassPPL(self.Cobj_obj().__class__, object))
        self.assertTrue(isSubclassPPL(self.Cobj2_Cojb().__class__, object))
        self.assertTrue(isSubclassPPL(self.Cobj2_Cojb().__class__, self.Cobj_obj))
        self.assertTrue(isSubclassPPL(self.C0().__class__, object))
        self.assertTrue(isSubclassPPL(self.C5_1().__class__, object))

    def test_issubclass_num(self):
        with self.assertRaises(TypeError):
            numSubclassPPL(None, int)
        with self.assertRaises(TypeError):
            numSubclassPPL(int, None)
        with self.assertRaises(TypeError):
            numSubclassPPL(1, 1)
        with self.assertRaises(TypeError):
            numSubclassPPL(1, int)
        with self.assertRaises(TypeError):
            numSubclassPPL(int, [int])

        self.assertEqual(numSubclassPPL(self.C0, self.C0), 1)
        self.assertEqual(numSubclassPPL(self.C1_0, self.C0), 2)
        self.assertEqual(numSubclassPPL(self.C2_0, self.C0), 2)
        self.assertEqual(numSubclassPPL(self.C1_0, self.C1_0), 1)
        self.assertEqual(numSubclassPPL(self.C2_0, self.C2_0), 1)
        self.assertEqual(numSubclassPPL(self.C3_12, self.C0), 3)
        self.assertEqual(numSubclassPPL(self.C3_12, self.C1_0), 2)
        self.assertEqual(numSubclassPPL(self.C3_12, self.C2_0), 2)
        self.assertEqual(numSubclassPPL(self.C3_12, self.C4_2), 0)
        self.assertEqual(numSubclassPPL(self.C4_2, self.C1_0), 0)
        self.assertEqual(numSubclassPPL(self.C5_1, self.C3_12), 0)
        self.assertEqual(numSubclassPPL(self.Cobj_obj, object), 2)
        self.assertEqual(numSubclassPPL(self.Cobj2_Cojb, object), 3)
        self.assertEqual(numSubclassPPL(self.Cobj2_Cojb, self.Cobj_obj), 2)
        self.assertEqual(numSubclassPPL(self.C0, object), 2)
        self.assertEqual(numSubclassPPL(self.C5_1, object), 4)

        self.assertEqual(numSubclassPPL(type(self.C0()), self.C0), 1)
        self.assertEqual(numSubclassPPL(type(self.C1_0()), self.C0), 2)
        self.assertEqual(numSubclassPPL(type(self.C2_0()), self.C0), 2)
        self.assertEqual(numSubclassPPL(type(self.C1_0()), self.C1_0), 1)
        self.assertEqual(numSubclassPPL(type(self.C2_0()), self.C2_0), 1)
        self.assertEqual(numSubclassPPL(type(self.C3_12()), self.C0), 3)
        self.assertEqual(numSubclassPPL(type(self.C3_12()), self.C1_0), 2)
        self.assertEqual(numSubclassPPL(type(self.C3_12()), self.C2_0), 2)
        self.assertEqual(numSubclassPPL(type(self.C3_12()), self.C4_2), 0)
        self.assertEqual(numSubclassPPL(type(self.C4_2()), self.C1_0), 0)
        self.assertEqual(numSubclassPPL(type(self.C5_1()), self.C3_12), 0)
        self.assertEqual(numSubclassPPL(type(self.Cobj_obj()), object), 2)
        self.assertEqual(numSubclassPPL(type(self.Cobj2_Cojb()), object), 3)
        self.assertEqual(numSubclassPPL(type(self.Cobj2_Cojb()), self.Cobj_obj), 2)
        self.assertEqual(numSubclassPPL(type(self.C0()), object), 2)
        self.assertEqual(numSubclassPPL(type(self.C5_1()), object), 4)

        self.assertEqual(numSubclassPPL(self.C0().__class__, self.C0), 1)
        self.assertEqual(numSubclassPPL(self.C1_0().__class__, self.C0), 2)
        self.assertEqual(numSubclassPPL(self.C2_0().__class__, self.C0), 2)
        self.assertEqual(numSubclassPPL(self.C1_0().__class__, self.C1_0), 1)
        self.assertEqual(numSubclassPPL(self.C2_0().__class__, self.C2_0), 1)
        self.assertEqual(numSubclassPPL(self.C3_12().__class__, self.C0), 3)
        self.assertEqual(numSubclassPPL(self.C3_12().__class__, self.C1_0), 2)
        self.assertEqual(numSubclassPPL(self.C3_12().__class__, self.C2_0), 2)
        self.assertEqual(numSubclassPPL(self.C3_12().__class__, self.C4_2), 0)
        self.assertEqual(numSubclassPPL(self.C4_2().__class__, self.C1_0), 0)
        self.assertEqual(numSubclassPPL(self.C5_1().__class__, self.C3_12), 0)
        self.assertEqual(numSubclassPPL(self.Cobj_obj().__class__, object), 2)
        self.assertEqual(numSubclassPPL(self.Cobj2_Cojb().__class__, object), 3)
        self.assertEqual(numSubclassPPL(self.Cobj2_Cojb().__class__, self.Cobj_obj), 2)
        self.assertEqual(numSubclassPPL(self.C0().__class__, object), 2)
        self.assertEqual(numSubclassPPL(self.C5_1().__class__, object), 4)


class TestFunctions(unittest.TestCase):
    def test_count_if(self):
        def positive(x):
            return x > 0

        self.assertEqual(count_if([1, 0, 8], lambda x: x > 2), 1)
        self.assertEqual(count_if([1, 1, 8], lambda x: x == 1), 2)
        self.assertEqual(count_if([1, 1, "a", "b"], lambda x: x == 1), 2)
        self.assertEqual(count_if([], lambda x: x == 0), 0)
        self.assertEqual(count_if([1, 2, 3], lambda x: x == 0), 0)

        self.assertEqual(count_if([1, 0, 8], positive), 2)
        self.assertEqual(count_if([1, 1, 8], positive), 3)
        self.assertEqual(count_if([], positive), 0)
        self.assertEqual(count_if([-1, -2, -3], positive), 0)

        with self.assertRaises(TypeError):
            self.assertEqual(count_if(None, positive), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(count_if([3], 3), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(count_if([3], None), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(count_if(3, positive), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(count_if("a", positive), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(count_if({"1": 1}, positive), 1)
        with self.assertRaises(TypeError):
            self.assertEqual(count_if((0, 1, 2), positive), 2)
        with self.assertRaises(TypeError):
            self.assertEqual(count_if([{"3": 3}, {"4": 4}], lambda x: x + 5), 2)

    def test_for_all(self):
        def positive(x):
            return x > 0

        def minus(x):
            return -x

        self.assertTrue(for_all([1, 1, 8], lambda x: x, lambda x: x > 0))
        self.assertTrue(for_all([8, 3, 8, 4, 58, 3], lambda x: x * 2, lambda x: x % 2 == 0))
        self.assertFalse(for_all([1, 0, 8], lambda x: x * 2, lambda x: x > 0))

        self.assertTrue(for_all([-11, -1, -8], minus, positive))
        self.assertFalse(for_all([8, 3, 8, 4, 58, 3], minus, positive))
        self.assertFalse(for_all([1, 0, 8], minus, positive))

        with self.assertRaises(TypeError):
            self.assertEqual(for_all(None, lambda x: x, lambda x: x > 0), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all([3, 5], None, lambda x: x > 0), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all([3, 5], lambda x: x, None), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all([3, 5], 3, lambda x: x > 0), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all([3, 5], lambda x: x, 3), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all(3, minus, positive), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all({"3": 3}, minus, positive), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all((3, 4), minus, positive), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all_red([{"3": 3}, {"3": 5}], minus, positive), 0)

    def test_for_all_red(self):
        def positive(x):
            return x > 0

        def plus(x, y):
            return x + y

        self.assertTrue(for_all_red([1, 1, 8], lambda x, y: x * y, lambda x: x > 7))
        self.assertFalse(for_all_red([1, 3, 5], lambda x, y: x * y, lambda x: x / 2 == 0))
        self.assertTrue(for_all_red([-10, 5, 7], plus, positive))
        self.assertFalse(for_all_red([-10, -5, 7], plus, positive))

        with self.assertRaises(TypeError):
            self.assertEqual(for_all_red(None, lambda x, y: x * y, lambda x: x > 7), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all_red([3, 5], None, lambda x: x > 7), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all_red([3, 5], lambda x, y: x * y, None), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all_red(3, 3, positive), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all_red(3, plus, 3), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all_red(3, plus, positive), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all_red({"3": 3}, plus, positive), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all_red((3, 4), plus, positive), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(for_all_red([{"3": 3}, {"3": 5}], plus, positive), 0)

    def test_there_exists(self):
        def positive(x):
            return x > 0

        self.assertTrue(there_exists([5, 3, 10], 3, positive))
        self.assertTrue(there_exists([5, 3, 10], 3, lambda x: x > 0))
        self.assertTrue(there_exists([5, 3, 10], 0, lambda x: x > 0))
        self.assertTrue(there_exists([5, 3, 10], 2, positive))
        self.assertTrue(there_exists([5, 3, 10], 2.5, positive))
        self.assertFalse(there_exists([5, 3, 10], 4, positive))
        self.assertFalse(there_exists([5, 3, 2], 5, lambda x: True))
        self.assertTrue(there_exists([5, 3, 2], 2, lambda x: True))

        with self.assertRaises(TypeError):
            self.assertEqual(there_exists(None, 5, lambda x: x > 7), False)
        with self.assertRaises(TypeError):
            self.assertEqual(there_exists([5], None, lambda x: x > 7), False)
        with self.assertRaises(TypeError):
            self.assertEqual(there_exists([5], 5, None), False)
        with self.assertRaises(TypeError):
            self.assertEqual(there_exists([5], -3, lambda x: x > 7), False)
        with self.assertRaises(TypeError):
            self.assertEqual(there_exists([5], "a", lambda x: x > 7), False)
        with self.assertRaises(TypeError):
            self.assertEqual(there_exists([5], 4, 5), 0)
        with self.assertRaises(TypeError):
            self.assertEqual(there_exists(5, 5, lambda x: x > 7), False)
        with self.assertRaises(TypeError):
            self.assertEqual(there_exists((5, 4), 5, lambda x: x > 7), False)
        with self.assertRaises(TypeError):
            self.assertEqual(there_exists({"5": 5}, 5, lambda x: x > 7), False)
        with self.assertRaises(TypeError):
            self.assertEqual(there_exists("5", 5, lambda x: x > 7), False)


if __name__ == '__main__':
    unittest.main()
