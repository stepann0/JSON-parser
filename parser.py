import re


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
        while self.next_unread_char in self.ws:
            self.read()

    def match(self, tok):
        """Check next unread char and advance"""
        if self.next_unread_char != tok:
            self.error(f"wrong token ('{self.next_unread_char}')")
        self.advance()

    def parse(self):
        json = self.parse_element()
        self.match(self.EOF)
        return json

    def parse_obj(self):
        obj = {}
        self.match("{")
        if self.next_unread_char == "}":
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
        return self.parse_value()

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

    def parse_array(self)-> list:
        arr = []
        self.match("[")
        if self.next_unread_char == "]":  # empty array
            return arr
        self.parse_elements(arr)
        self.match("]")
        return arr
        
    def parse_elements(self, arr):
        arr.append(self.parse_element())
        if self.next_unread_char == ",":
            self.advance()
            self.parse_elements(arr)
    
    def parse_number(self)-> int|float:
        r"""re: -?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?"""
        # NOTE: simplest implementation only as start point
        num = ""
        while self.next_unread_char in self.number_start+[".", "e", "E", "+"]:
            num += self.next_unread_char
            self.advance()
        return int(num) if "." not in num else float(num)

    def parse_string(self)-> str:
        r"""re: /"(?>\\(?>["\\\/bfnrt]|u[a-fA-F0-9]{4})|[^"\\\0-\x1F\x7F]+)*"/gm"""
        # NOTE: simplest implementation only as start point
        self.match('"')
        string = ""
        while self.next_unread_char != '"':
            string += self.next_unread_char
            self.advance()
        self.match('"')
        return string

    def parse_num(self)-> int:
        """num:  '0'
                |'1..9' follow_dig"""
        if self.next_unread_char in self.one_nine:
            n = int(self.next_unread_char)
            self.advance()
            return self.parse_follow_dig(n)
        elif self.next_unread_char == '0':
            self.advance()
            return 0
        else:
            self.error("parse number")

    def parse_follow_dig(self, n: int)-> int:
        """follow_dig: '0..9' follow_dig
                       |ε"""
        if self.next_unread_char in self.zero_nine:
            n = n * 10 + int(self.next_unread_char)
            self.advance()
            return self.parse_follow_dig(n)
        return n

    def parse_nums(self)-> list[int]:
        """nums:  num next_num
                 |ε"""
        arr = []
        if self.next_unread_char not in self.one_nine+[","]:
            return arr
        arr.append(self.parse_num())
        self.parse_next_num(arr)
        return arr

    def parse_next_num(self, arr):
        """next_num:  ',' num next_num
                     |ε"""
        while self.next_unread_char == ",":
            self.advance()
            arr.append(self.parse_num())

    def parse_arr(self)-> list[int]:
        """arr: '[' nums ']'"""
        self.match("[")
        arr = self.parse_nums()
        self.match("]")
        self.match(self.EOF)

        print(f"Correct! {sorted(arr)}")
        return arr

    def error(self, msg):
        print(f"Syntax error: {msg}")
        print(self.expr)
        print(f"{'~'*self.pos}^")
        exit(1)

p = Parser('{"a": 4, "b": 5, "c": null, "d": [true, false]}')
print(p.parse())