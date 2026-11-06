"""一个简单的计算器模块，用来练习 CI/CD。"""


def add(a: float, b: float) -> float:
    """返回 a + b。"""
    return a + b


def subtract(a: float, b: float) -> float:
    """返回 a - b。"""
    return a - b


def multiply(a: float, b: float) -> float:
    """返回 a * b。"""
    return a * b


def divide(a: float, b: float) -> float:
    """返回 a / b；b 为 0 时抛出 ValueError。"""
    if b == 0:
        raise ValueError("除数不能为 0")
    return a / b
