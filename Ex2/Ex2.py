# region Q1
from math import sqrt


class ComplexNum:
    def __init__(self, re, im):
        ComplexNum.__assert_type(isinstance(re, (float, int)), "Real number is not a number")
        ComplexNum.__assert_type(isinstance(im, (float, int)), "Imaginary number is not a number")
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
        ComplexNum.__assert_type(isinstance(other, ComplexNum), "Complex comparison only defined for Complex Numbers.")
        return self.re() == other.re() and self.im() == other.im()

    def __add__(self, other):
        ComplexNum.__assert_type(isinstance(other, ComplexNum), "Complex addition only defined for Complex Numbers.")
        re_sum = self.re() + other.re()
        im_sum = self.im() + other.im()
        return ComplexNum(re=re_sum, im=im_sum)

    def __neg__(self):
        return ComplexNum(-self.re(), -self.im())

    def __sub__(self, other):
        ComplexNum.__assert_type(isinstance(other, ComplexNum), "Complex subtraction only defined for Complex Numbers.")
        return self + (-other)

    def __mul__(self, other):
        ComplexNum.__assert_type(isinstance(other, ComplexNum), "Complex multiplication only defined for Complex Numbers.")
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

    @staticmethod
    def __assert_type(condition, message):
        if not condition:
            raise TypeError(message)


# endregion

# region Q2
def isInstancePPL(object1, classInfo):
    current = object1
    while type(current) is not classInfo:
        current = current.parent

# endregion
