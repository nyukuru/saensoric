from enum import Enum
from abc import ABCMeta

class Type(Enum):
    VOID = 0
    INT = 1
    BOOL = 2
    STRING = 3

class Function:
    def __init__(self, name, args, var, fun, body, deco=None):
        self.name = name
        self.args = args
        self.var = var
        self.fun = fun
        self.body = body
        self.deco = deco or {}

class Print:
    def __init__(self, expr: str, newline: str, deco: dict[str, str] | None = None):
        self.newline: str = newline
        self.expr: str = expr
        self.deco: dict[str, str] = deco or {}

class Return:
    def __init__(self, expr: str, deco: dict[str, str] | None = None):
        self.expr: str = expr
        self.deco: dict[str, str] = deco or {}

class Assign:
    def __init__(self, expr: str, name: str, deco: dict[str, str] | None = None):
        self.name: str = name
        self.expr: str = expr
        self.deco: dict[str, str] = deco or {}

class While:
    def __init__(self, expr: str, body: str, deco: dict[str, str] | None = None):
        self.body: str = body 
        self.expr: str = expr
        self.deco: dict[str, str] = deco or {}

class IfThenElse:
    def __init__(self, expr: str, ibody: str, ebody: str, deco: dict[str, str] | None = None):
        self.ibody: str = ibody 
        self.ebody: str = ebody
        self.expr: str = expr
        self.deco: dict[str, str] = deco or {}

class ArithOp:
    def __init__(self, op, left, right, deco: dict[str, str] | None = None):
        self.op: str = op
        self.left: str = left
        self.right: str = right
        self.deco: dict[str, str] = deco or {}

class LogicOp:
    def __init__(self, op, left, right, deco: dict[str, str] | None = None):
        self.op: str = op
        self.left: str = left
        self.right: str = right
        self.deco: dict[str, str] = deco or {}

class Integer:
    def __init__(self, value, deco: dict[str, str] | None = None):
        self.value = value
        self.deco = deco or {}

class Boolean:
    def __init__(self, value, deco: dict[str, str] | None = None):
        self.value = value
        self.deco = deco or {}

class String:
    def __init__(self, value, deco: dict[str, str] | None = None):
        self.value = value
        self.deco = deco or {}

class Var:
    def __init__(self, name, deco: dict[str, str] | None = None):
        self.name = name
        self.deco = deco or {}

class FunCall:
    def __init__(self, name, args, deco: dict[str, str] | None = None):
        self.name = name
        self.args = args
        self.deco = deco or {}
