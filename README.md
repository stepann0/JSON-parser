## Простой JSON парсер (декодер)

Использует алгоритм рекурсивного спуска.

Пример:
```python
 decoder = JSONDecoder("""{
  "a": true,
  "b": false,
  "c": null,
  "d": {
    "e": 1,
    "f": -2205
  },
  "g": [
    0,
    99879.5645e-3,
    false,
    "string",
    ""
  ]
}""")
obj = decoder.decode()
print(obj)

{'a': True, 'b': False, 'c': None, 'd': {'e': 1, 'f': -2205}, 'g': [0, 99.8795645, False, 'string', '']}
```
