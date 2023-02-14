class JSONDecodeError(ValueError):
    def __init__(self, msg, doc, pos):
        lineno = doc.count('\n', 0, pos) + 1
        colno = pos - doc.rfind('\n', 0, pos)
        errmsg = '%s: line %d column %d (char %d)' % (msg, lineno, colno, pos)
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.lineno = lineno
        self.colno = colno

    def __reduce__(self):
        return self.__class__, (self.msg, self.doc, self.pos)


class Parser:
    def __init__(self, expr: str):
        self.EOF = ""
        self.ws = list(" \t\n\r")
        self.zero_nine = list("0123456789")
        self.one_nine = list("123456789")
        self.number_start = ["-"] + self.zero_nine

        self.expr = expr
        self.pos = 0
        self.next_unread_char = self.next()

    def read(self, n=1):
        """Read n chars from input and return them"""

        new_pos = self.pos + n
        res = self.expr[self.pos:new_pos]
        self.pos = new_pos
        self.next_unread_char = self.next()
        return res

    def next(self):
        """Return next unread char in input of EOF"""
        return self.expr[self.pos] if self.pos < len(self.expr) else self.EOF

    def advance(self):
        """Read one char from input and skip white spaces"""
        self.read()
        self.skip_ws()

    def match(self, tok):
        """Check next unread char and advance"""
        if self.next_unread_char != tok:
            self.error(f"wrong token ('{self.next_unread_char}')")
        self.advance()

    def skip_ws(self):
        while self.next_unread_char in self.ws:
            self.read()

    def parse(self):
        json = self.parse_element()
        self.match(self.EOF)
        return json

    def parse_obj(self) -> dict:
        obj = {}
        self.match("{")
        if self.next_unread_char == "}":
            self.advance()
            return obj
        self.parse_members(obj)
        self.match("}")
        return obj

    def parse_members(self, obj):
        member = self.parse_member()
        obj[member[0]] = member[1]
        if self.next_unread_char == ",":
            self.advance()
            self.parse_members(obj)

    def parse_member(self):
        member_key = self.parse_string()
        self.match(":")
        member_value = self.parse_element()
        return member_key, member_value

    def parse_element(self):
        self.skip_ws()
        val = self.parse_value()
        self.skip_ws()
        return val

    def parse_value(self):
        if self.next_unread_char == '{':
            return self.parse_obj()
        elif self.next_unread_char == '[':
            return self.parse_array()
        elif self.next_unread_char == '"':
            return self.parse_string()
        elif self.next_unread_char in self.number_start:
            return self.parse_number()
        elif self.next_unread_char == 't':  # true
            if self.read(4) != "true":
                self.error("parse 'true'")
            return True
        elif self.next_unread_char == 'f':  # false
            if self.read(5) != "false":
                self.error("parse 'false'")
            return False
        elif self.next_unread_char == 'n':  # null
            if self.read(4) != "null":
                self.error("parse 'null'")
            return None
        else:
            self.error("parse value")

    def parse_array(self) -> list:
        arr = []
        self.match("[")
        if self.next_unread_char == "]":  # empty array
            self.advance()
            return arr
        self.parse_elements(arr)
        self.match("]")
        return arr

    def parse_elements(self, arr):
        arr.append(self.parse_element())
        if self.next_unread_char == ",":
            self.advance()
            self.parse_elements(arr)

    def parse_string(self) -> str:
        r"""re: /"(?>\\(?>["\\\/bfnrt]|u[a-fA-F0-9]{4})|[^"\\\0-\x1F\x7F]+)*"/gm"""
        # NOTE: simplest implementation only as start point
        self.match('"')
        string = ""
        while self.next_unread_char != '"':
            string += self.next_unread_char
            self.advance()
        self.match('"')
        return string

    def parse_number(self):
        return (self.parse_int() + self.parse_fraction()) * 10 ** self.parse_exponent()

    def parse_int(self):
        """Parse integer and return it"""
        if self.next_unread_char == "-":
            self.read()
            return -1*self.parse_one_or_more_digits()
        return self.parse_one_or_more_digits()

    def parse_one_or_more_digits(self) -> int:
        if self.next_unread_char == '0':
            self.advance()
            return 0
        if self.next_unread_char in self.one_nine:
            return int(self.read()+self.read_digits(0))
        self.error("parse number")

    def read_digits(self, min_count) -> str:
        """Read at least min_count digits and return string"""
        digits = ""
        while self.next_unread_char in self.zero_nine:
            digits += self.read()
        if len(digits) < min_count:
            self.error(f"expected {min_count} or more digits")
        return digits

    def parse_fraction(self) -> float:
        if self.next_unread_char == '.':
            return float(self.read() + self.read_digits(1))
        return 0

    def parse_exponent(self) -> int:
        if self.next_unread_char in ["e", "E"]:
            self.read()
            sign = 1
            if self.next_unread_char == "+":
                self.read()
            elif self.next_unread_char == "-":
                sign = -1
                self.read()
            return sign*int(self.read_digits(1))
        return 0

    def error(self, msg):
        raise JSONDecodeError(msg, self.expr, self.pos)


json = """{"a":[3,,4]}"""
p = Parser(json)
obj = p.parse()
print(obj)
