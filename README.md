## Простой JSON парсер

Использует алгоритм рекурсивного спуска.

Пример:
```python
p = Parser('{"a": true, "b": false, "c": null, "d": {"e": 1, "f": -22.05e+2}, "g": [0, 99879.5645e-4, false, "string", ""]}')
obj = p.parse()
print(obj)

{'a': True, 'b': False, 'c': None, 'd': {'e': 1, 'f': -2195.0}, 'g': [0, 9.98795645, False, 'string', '']}
```
