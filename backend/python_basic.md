# Python 基础知识

## 1. Python 是什么？

Python 是一种简单易学的高级编程语言，广泛应用于 Web 开发、数据分析、人工智能和自动化脚本等领域。

## 2. Python 常见数据类型

Python 中常见的数据类型包括：

- `int`：整数，例如 `10`
- `float`：浮点数，例如 `3.14`
- `str`：字符串，例如 `"Hello"`
- `bool`：布尔值，例如 `True` 和 `False`
- `list`：列表，例如 `[1, 2, 3]`
- `dict`：字典，例如 `{"name": "Tom"}`

## 3. 列表的增加和删除

列表（List）是一种可以存储多个元素的数据结构。

### 增加元素

- `append()`：在列表末尾增加一个元素。
- `insert()`：在指定位置插入一个元素。
- `extend()`：将另一个可迭代对象中的元素添加到列表末尾。

示例：

```python
numbers = [1, 2, 3]

numbers.append(4)
numbers.insert(0, 0)
numbers.extend([5, 6])

print(numbers)
```

### 删除元素

- `remove()`：删除指定值。
- `pop()`：删除指定位置的元素，并返回该元素。
- `clear()`：清空整个列表。

示例：

```python
numbers = [1, 2, 3, 4]

numbers.remove(2)
numbers.pop()
numbers.clear()
```

## 4. Python 函数

使用 `def` 关键字可以定义函数。

```python
def add(a, b):
    return a + b

result = add(3, 5)
print(result)
```

这个函数接收两个参数，并返回它们的和。

## 5. 总结

Python 提供了丰富的数据类型和内置方法。掌握列表操作、函数定义和基本数据类型，是学习 Python 编程的重要基础。