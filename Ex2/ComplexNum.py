class ComplexNum:
    def __init__(self, re, im):
        assert isinstance(re, (float, int)), "Real number is not a number"
        assert isinstance(im, (float, int)), "Imaginary number is not a number"
        self._re = re
        self._im = im

    def __repr__(self):
        if self._re == 0 and self._im == 0:
            return "0"
        re_str = "" if self._re == 0 else str(self._re)
        im_str = "" if self._im == 0 else str(abs(self._im)) + "i"
        if self._re != 0 and self._im > 0:
            sign = " + "
        elif self._re != 0 and self._im < 0:
            sign = " - "
        elif self._re == 0 and self._im < 0:
            sign = "-"
        else:
            sign = ""
        return "{0}{1}{2}".format(re_str, sign, im_str)

    def __eq__(self, other):
        pass

    def __add__(self, other):
        pass

    def __neg__(self):
        pass

    def __sub__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __abs__(self):
        pass

    def re(self):
        return self._re

    def im(self):
        return self._im

    def to_tuple(self):
        return self._re, self._im

    def conjugate(self):
        pass
