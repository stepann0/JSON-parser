from parser import Parser

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
        P = Parser(k)
        assert P.parse_value() == v

def test_parse_number():
    ints = ["123456", "0", "1", "2", "5", "-54321", "-9", "-8", "-0", "1000002", "500000"]
    for n in ints:
        P = Parser(n)
        assert P.parse_number() == int(n)

    floats = ["123.0", "-2345.0", "0.0005e+3", "98769e-2", "-0.0", "1.0405006E+005"]
    for n in floats:
        P = Parser(n)
        assert P.parse_number() == float(n.lower())  # 'e', not 'E'
