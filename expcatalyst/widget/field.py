# -*- coding: utf-8 -*-


__all__ = [
    "BaseField",
    "BooleanField",
    "LineField",
    "TextField",
    "IntegerField",
    "FloatField",
    "FileField",
    # "FilePathField",
    # "EmailField",
    # "URLField",
    # "ListField",
    "ChoiceField",
]


# ----------------------------------------------
class BaseField(object):
    def __init__(self, key, label, *args, **kwargs):
        self.key = key
        self.label = label
        self.args = args
        self.kwargs = kwargs

    def Validate(self, value):
        pass


# ----------------------------------------------
class BooleanField(BaseField):
    def __init__(self, key, label, tag1, tag2, *args, **kwargs):
        super().__init__(key=key, label=label, *args, **kwargs)
        self.tag1 = tag1
        self.tag2 = tag2

    def Validate(self, value):
        return value


# ----------------------------------------------
class LineField(BaseField):
    def __init__(self, key, label, maxLength=None, minLength=None, hint="", *args, **kwargs):
        super().__init__(key=key, label=label, *args, **kwargs)
        self.hint = hint
        self.maxLength = maxLength
        self.minLength = minLength

    def Validate(self, value):
        length = len(value)
        if self.maxLength is not None and length > self.maxLength:
            return None
        if self.minLength is not None and length < self.minLength:
            return None
        return value


# ----------------------------------------------
class TextField(BaseField):
    def __init__(self, key, label, maxLine=None, minLine=None, maxLength=None, minLength=None, *args, **kwargs):
        super().__init__(key=key, label=label, *args, **kwargs)
        self.maxLine = maxLine
        self.minLine = minLine
        self.maxLength = maxLength
        self.minLength = minLength

    def Validate(self, value):
        length = len(value)
        line = value.count("\n") + 1
        if self.maxLength is not None and length > self.maxLength:
            return None
        if self.minLength is not None and length < self.minLength:
            return None
        if self.maxLine is not None and line > self.maxLine:
            return None
        if self.minLine is not None and line < self.minLine:
            return None
        return value


# ----------------------------------------------
class IntegerField(BaseField):
    def __init__(self, key, label, maxValue=None, minValue=None, *args, **kwargs):
        super().__init__(key=key, label=label, *args, **kwargs)
        self.maxValue = maxValue
        self.minValue = minValue

    def Validate(self, value):
        if isinstance(value, str) and value != "":
            if value.isdigit() or (value[0] in ("-", "+") and value[1:].isdigit()):
                value = int(value)
                if self.maxValue is not None and value > self.maxValue:
                    return None
                if self.minValue is not None and value < self.minValue:
                    return None
                return value
        elif isinstance(value, int):
            return value
        return None


# ----------------------------------------------
class FloatField(BaseField):
    def __init__(self, key, label, maxValue=None, minValue=None, *args, **kwargs):
        super().__init__(key=key, label=label, *args, **kwargs)
        self.maxValue = maxValue
        self.minValue = minValue

    def Validate(self, value):
        try:
            value = float(value)
            if self.maxValue is not None and value > self.maxValue:
                return None
            if self.minValue is not None and value < self.minValue:
                return None
            return value
        except ValueError:
            return None


# ----------------------------------------------
class ChoiceField(BaseField):
    def __init__(self, key, label, choices=(), useListBox=False, *args, **kwargs):
        super().__init__(key=key, label=label, *args, **kwargs)
        self.choices = choices
        self.useListBox = useListBox

    def Validate(self, value):
        if value < 0:
            return None
        if value >= len(self.choices):
            return None
        return self.choices[value]


# ----------------------------------------------
class FileField(BaseField):
    def __init__(self, key, label, *args, **kwargs):
        super().__init__(key=key, label=label, *args, **kwargs)

    def Validate(self, value):
        return value

# ----------------------------------------------
# class FilePathField(BaseField):
#     def __init__(self, key, label, exist=None):
#         super().__init__(key=key, label=label)
#         self.exist = exist


# ----------------------------------------------
# class EmailField(BaseField):
#     PATTERN = re.compile("[^@]+@[^@]+\.[^@]+")
#
#     def __init__(self, key, label, maxLength=None, minLength=None):
#         super().__init__(key=key, label=label)
#         self.maxLength = maxLength
#         self.minLength = minLength
#
#     def Validate(self, value):
#         length = len(value)
#         if self.maxLength is not None and length > self.maxLength:
#             return None
#         if self.minLength is not None and length < self.minLength:
#             return None
#         if not self.PATTERN.match(value):
#             return None
#         return value


# ----------------------------------------------
# class URLField(BaseField):
#     def __init__(self, key, label):
#         super().__init__(key=key, label=label)


# ----------------------------------------------
# class ListField(BaseField):
#     def __init__(self, key, label, choices=(), basefield=LineField, multiple=False):
#         super().__init__(key=key, label=label)
#         self.choices = choices
#         self.multiple = multiple
