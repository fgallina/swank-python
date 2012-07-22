import logging
import re


__all__ = ['BOOL_PATTERN', 'NUMBER_PATTERN', 'cons', 'lbool', 'llist',
           'lstring', 'quoted', 'symbol', 'DOT_OPERATOR', 'LispReader',
           'LispWritter', 'read_lisp', 'write_lisp']


logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s')


BOOL_PATTERN = re.compile(r"^('?t|'?nil)\b")
NUMBER_PATTERN = re.compile(r"^([0-9]+(\.[0-9]+)?)\b[^.]")


class cons(object):
    """Simple type representing a cons cell."""

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __repr__(self):
        return "cons({0}, {1})".format(self.car, self.cdr)

    def __str__(self):
        return "({0} . {1})".format(self.car, self.cdr)


class lbool(object):
    """Simple list type representing a cons cell."""

    def __init__(self, value):
        self.value = bool(value)

    def __repr__(self):
        return "lbool(" + str(self.value) + ")"

    def __str__(self):
        if self.value:
            return "t"
        else:
            return "nil"


class llist(list):
    """Simple list type representing a lisp list."""

    def __repr__(self):
        return "llist(" + super(llist, self).__repr__() + ")"

    def __str__(self):
        parts = []
        for part in self:
            parts.append(str(part))
        return "(" + ' '.join(parts) + ")"


class lstring(str):
    """Simple string type representing a lisp string."""

    def __repr__(self):
        return "lstring(" + super(lstring, self).__repr__() + ")"

    def __str__(self):
        return '"' + self + '"'


class quoted(llist):
    """Simple list type representing a quoted lisp list."""

    def __repr__(self):
        return "quoted(" + super(quoted, self).__repr__() + ")"

    def __str__(self):
        return "'" + super(quoted, self).__str__()


class symbol(str):
    """Simple string type representing a lisp symbol."""

    def __repr__(self):
        return "symbol(" + super(symbol, self).__repr__() + ")"

    def __str__(self):
        return self


DOT_OPERATOR = symbol(".")


class LispReader(object):

    def __init__(self, code):
        self.code = code
        self.char_pos = 0
        self.logger = logging.getLogger('LispReader')

    def char_at_pos(self, pos):
        try:
            return self.code[pos]
        except IndexError:
            return ""

    def prev_char(self):
        return self.char_at_pos(self.char_pos - 1)

    def current_char(self):
        return self.char_at_pos(self.char_pos)

    def next_char(self):
        return self.char_at_pos(self.char_pos + 1)

    def remaining_code(self):
        return self.code[self.char_pos:]

    def read(self):
        try:
            self.skip_whitespace()
            char = self.current_char()
            next_char = self.next_char()
            if char == "(" or (char == "'" and next_char == "("):
                return self.read_list()
            elif char == '"':
                return self.read_string()
            elif char == ";":
                self.skip_comment()
                return self.read()
            elif re.search(BOOL_PATTERN, self.remaining_code()):
                return self.read_bool()
            elif re.search(NUMBER_PATTERN, self.remaining_code()):
                return self.read_number()
            else:
                return self.read_symbol()
        except Exception as e:
            self.logger.debug("Parsing failed at: %s", self.remaining_code())
            raise

    def read_bool(self):
        starting_pos = self.char_pos
        if self.current_char() == "'":
            self.char_pos += 1
        if self.current_char() == "t":
            self.char_pos += 1
            return lbool(True)
        else:
            self.char_pos += 3
            return lbool(False)

    def read_list(self):
        char = self.current_char()
        quote = False
        if char == "'":
            collect = quoted()
            self.char_pos += 1
        else:
            collect = llist()
        self.char_pos += 1
        while True:
            if char != ")" and len(char):
                collect.append(self.read())
                char = self.current_char()
            else:
                break
        self.char_pos += 1
        # If this is a cons cell, return it.
        if DOT_OPERATOR in collect and len(collect) == 3:
            return cons(collect[0], collect[2])
        return collect

    def read_number(self):
        starting_pos = self.char_pos
        allowed = ["0", "1","2","3","4","5","6","7","8","9","."]
        char = self.current_char()
        is_float = False
        while char in allowed:
            if char == ".":
                is_float = True
            self.char_pos += 1
            char = self.current_char()
        number = self.code[starting_pos:self.char_pos]
        if is_float:
            return float(number)
        else:
            return int(number)

    def skip_whitespace(self):
        """Move char_pos to first non-whitespace char."""
        while self.current_char().isspace() and self.remaining_code():
            self.char_pos += 1

    def skip_comment(self):
        """Move char_pos to first non-whitespace char."""
        while self.current_char() != "\n" and self.remaining_code():
            self.char_pos += 1

    def read_string(self):
        starting_pos = self.char_pos + 1
        self.char_pos = starting_pos + 1
        char = self.current_char()
        prev_char = self.prev_char()
        while char != '"' or (char == '"' and prev_char == '\\'):
            try:
                self.char_pos += 1
                char = self.code[self.char_pos]
                prev_char = self.prev_char()
            except IndexError:
                raise ValueError(
                    "Unterminated string literal at {0}".format(self.char_pos))
        string = self.code[starting_pos:self.char_pos]
        self.char_pos += 1
        return lstring(string)

    def read_symbol(self):
        starting_pos = self.char_pos
        char = self.current_char()
        while char and not char.isspace() and char != ")":
            self.char_pos += 1
            char = self.current_char()
        string = self.code[starting_pos:self.char_pos]
        return symbol(string)


class LispWritter(object):

    def __init__(self, value):
        self.value = value

    def to_lisp_string(self, obj):
        if isinstance(obj, (cons, lbool, llist, lstring, quoted, symbol)):
            return str(obj)
        elif isinstance(obj, str):
            return '"' + str(obj) + '"'
        elif isinstance(obj, (float, int)):
            return str(obj)
        elif obj is None or isinstance(obj, bool):
            return str(lbool(obj))
        elif isinstance(obj, (list, tuple)):
            parts = []
            for part in obj:
                parts.append(self.to_lisp_string(part))
            return "(" + ' '.join(parts) + ")"
        elif isinstance(obj, dict):
            parts = []
            for key, value in obj.items():
                parts.append(self.to_lisp_string(symbol(key)))
                parts.append(self.to_lisp_string(value))
            return "(" + ' '.join(parts) + ")"
        else:
            return str(obj)

    def write(self):
        return self.to_lisp_string(self.value)


def read_lisp(code):
    return LispReader(code).read()


def write_lisp(value):
    return LispWritter(value).write()
