import re


class Parser:
    def __init__(self, expr: str):
        self.pos = 0
        self.EOF = ""
        self.ws = list(" \t\n\r")
        self.zero_nine = list("0123456789")
        self.one_nine = list("123456789")
        self.number_start = ["-"] + self.one_nine

        self.expr = expr
        self.next_unread_char = self.new_read()

    def read(self, n=1):
        new_pos = self.pos + n
        res = self.expr[self.pos:new_pos]
        self.pos = new_pos
        self.next_unread_char = self.expr[self.pos] if self.pos < len(self.expr) else self.EOF
        
        print(f"read '{res}', next unread: '{self.next_unread_char}', curr pos: {self.pos}")
        return res

    def new_read(self):
        res = self.EOF
        if self.pos < len(self.expr):
            res = self.expr[self.pos]
        self.pos += 1
        return res

    def advance(self):
        self.next_unread_char = self.new_read()
        while self.next_unread_char in self.ws:
            self.next_unread_char = self.new_read()

    def match(self, tok):
        if self.next_unread_char != tok:
            self.error(f"wrong token ('{self.next_unread_char}')")
        self.advance()

    def parse_obj(self):
        self.match("{")
        self.parse_member()
        self.match("}")

    def parse_member(self):
        self.parse_string()
        self.match(":")
        self.parse_element()

    def parse_element(self):
        self.parse_value()

    def parse_value(self):
        if self.next_unread_char == '{':
            self.parse_obj()
        elif self.next_unread_char == '[':
            self.parse_array()
        elif self.next_unread_char == '"':
            self.parse_string()
        elif self.next_unread_char in self.number_start:
            self.parse_number()
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

    def parse_array(self):
        self.match("[")
        if self.next_unread_char == "]":  # empty array
            return
        self.parse_elements()
        self.match("]")
        
    def parse_elements(self):
        self.parse_element()
        if self.next_unread_char == ",":
            self.parse_elements()
    
    def parse_number(self)-> int|float:
        """re: -?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?"""
        m = re.match(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?",
                     self.expr[self.pos:])
        return float(self.read(m.span()[1]-m.span()[0]))

    def parse_string(self):
        """re: /"(?>\\(?>["\\\/bfnrt]|u[a-fA-F0-9]{4})|[^"\\\0-\x1F\x7F]+)*"/gm"""
        # NOTE: simplest implementation only for now 
        self.match('"')
        string = ""
        while self.next_unread_char != '"':
            string += self.new_read()
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
        exit(1)


    

p = Parser("\"atr\"")
def read(n=1):
    print(f"read '{p.read(n)}', next unread: '{p.next_unread_char}' at {p.pos}, curr pos: {p.pos}")

p.parse_string()