from math import sqrt
import types
import collections


# region Q1


class ComplexNum:
    def __init__(self, re, im):
        assert_type(isinstance(re, (float, int)), "Real number is not a number")
        assert_type(isinstance(im, (float, int)), "Imaginary number is not a number")
        self._re = re
        self._im = im

    def __repr__(self):
        if self.re() == 0 and self.im() == 0:
            return "0"
        re_str = "" if self.re() == 0 else str(self.re())
        im_str = "" if self.im() == 0 else str(abs(self.im())) + "i"
        if self.re() != 0 and self.im() > 0:
            sign = " + "
        elif self.re() != 0 and self.im() < 0:
            sign = " - "
        elif self.re() == 0 and self.im() < 0:
            sign = "-"
        else:
            sign = ""
        return "{0}{1}{2}".format(re_str, sign, im_str)

    def __eq__(self, other):
        assert_type(isinstance(other, ComplexNum), "Complex comparison only defined for Complex Numbers.")
        return self.re() == other.re() and self.im() == other.im()

    def __add__(self, other):
        assert_type(isinstance(other, ComplexNum), "Complex addition only defined for Complex Numbers.")
        re_sum = self.re() + other.re()
        im_sum = self.im() + other.im()
        return ComplexNum(re=re_sum, im=im_sum)

    def __neg__(self):
        return ComplexNum(-self.re(), -self.im())

    def __sub__(self, other):
        assert_type(isinstance(other, ComplexNum), "Complex subtraction only defined for Complex Numbers.")
        return self + (-other)

    def __mul__(self, other):
        assert_type(isinstance(other, ComplexNum),
                    "Complex multiplication only defined for Complex Numbers.")
        re_mul = self.re() * other.re() - self.im() * other.im()
        im_mul = self.re() * other.im() + self.im() * other.re()
        return ComplexNum(re=re_mul, im=im_mul)

    def __abs__(self):
        mul = self * self.conjugate()
        return sqrt(mul.re())

    def abs(self):
        return abs(self)

    def re(self):
        return self._re

    def im(self):
        return self._im

    def to_tuple(self):
        return self.re(), self.im()

    def conjugate(self):
        return ComplexNum(self.re(), -self.im())


# endregion

# region Q2
def isInstanceRecursive(obj_class, class_info):
    if obj_class is class_info:
        return 1
    for base in obj_class.__bases__:
        distance = isInstanceRecursive(base, class_info)
        if distance > 0:
            return distance + 1
    return 0


def isInstancePPL(object1, classInfo):
    assert_type(object1 is not None, "Object must not be None")
    assert_type(type(classInfo) is types.ClassType or type(classInfo) is types.TypeType,
                "ClassInfo must be classobj or type type")
    return isInstanceRecursive(obj_class=object1.__class__, class_info=classInfo) > 0


def numInstancePPL(object1, classInfo):
    assert_type(object1 is not None, "Object must not be None")
    assert_type(type(classInfo) is types.ClassType or type(classInfo) is types.TypeType,
                "ClassInfo must be classobj or type type")
    return isInstanceRecursive(obj_class=object1.__class__, class_info=classInfo)


def isSubclassPPL(class_class, classInfo):
    assert_type(type(class_class) is types.ClassType or type(
        class_class) is types.TypeType, "class must be class or type type")
    assert_type(type(classInfo) is types.ClassType or type(classInfo) is types.TypeType,
                "ClassInfo must be classobj or type type")
    return isInstanceRecursive(obj_class=class_class, class_info=classInfo) > 0


def numSubclassPPL(class_class, classInfo):
    assert_type(type(class_class) is types.ClassType or type(
        class_class) is types.TypeType, "class must be class or type type")
    assert_type(type(classInfo) is types.ClassType or type(classInfo) is types.TypeType,
                "ClassInfo must be classobj or type type")
    return isInstanceRecursive(obj_class=class_class, class_info=classInfo)


# endregion

# region Q3
def count_if(lst, func):
    assert_type(isinstance(lst, list), "Passed object must be of type list")
    assert_type(isinstance(func, types.FunctionType), "Passed function must be of type function")
    try:
        return len(filter(func, lst))
    except:
        return -1


def for_all(lst, apply, pred):
    assert_type(isinstance(lst, list), "Passed object must be of type list")
    assert_type(isinstance(apply, types.FunctionType) and isinstance(pred, types.FunctionType),
                "Passed functions must be of type function")
    try:
        applied = map(apply, lst)
        return len(filter(pred, applied)) == len(lst)
    except:
        return False


def for_all_red(lst, apply, pred):
    assert_type(isinstance(lst, list), "Passed object must be of type list")
    assert_type(isinstance(apply, types.FunctionType) and isinstance(pred, types.FunctionType),
                "Passed functions must be of type function")
    try:
        reduced = reduce(apply, lst)
        return len(filter(pred, [reduced])) > 0
    except:
        return False


def there_exists(lst, n, pred):
    assert_type(isinstance(lst, list), "Passed object must be of type list")
    assert_type(isinstance(pred, types.FunctionType), "Passed function must be of type function")
    assert_type(isinstance(n, (float, int)), "n must be a non-negative number")
    assert_type(n >= 0, "n must be a non-negative number")
    try:
        return len(filter(pred, lst)) >= n
    except:
        return False


# endregion

def assert_type(condition, message):
    if not condition:
        raise TypeError(message)
