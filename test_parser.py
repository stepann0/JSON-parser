from decoder import JSONDecoder


def test_parse_value():
    values = {
        "true": True,
        "false": False,
        "null": None,
        '["", "true", "false", "string", "123.5E-6"]': ["", "true", "false", "string", "123.5E-6"],
        '[1, -0, 123.5E-6, 0.78e+9]': [1, -0, 123.5E-6, 0.78e+9],
        "[true, false, null]": [True, False, None],
        "[]": []
    }
    for k, v in values.items():
        d = JSONDecoder(k)
        assert d.parse_value() == v


def test_parse_number():
    ints = ["123456", "0", "1", "2", "5", "-54321",
            "-9", "-8", "-0", "1000002", "500000"]
    for n in ints:
        d = JSONDecoder(n)
        assert d.parse_number() == int(n)

    floats = ["123.0", "-2345.0", "0.0005e+3",
              "98769e-2", "-0.0", "1.0405006E+005"]
    for n in floats:
        d = JSONDecoder(n)
        assert round(d.parse_number(), 5) == float(n.lower())  # 'e', not 'E'


def test_parse_member():
    pairs = {
        '"a":true': ("a", True),
        '"b":0': ("b", 0),
        '"":null': ("", None),
        '"key":{}': ("key", {})
    }
    for k, v in pairs.items():
        d = JSONDecoder(k)
        assert d.parse_member() == v


def test_parse_array():
    arrays = {
        "[]": [],
        "[true,\nfalse,\nnull,\n{}]": [True, False, None, {}],
        "[\t1,\t2,\t\"string\", 34, 5.3]": [1, 2, "string", 34, 5.3]
    }
    for k, v in arrays.items():
        d = JSONDecoder(k)
        assert d.parse_array() == v
