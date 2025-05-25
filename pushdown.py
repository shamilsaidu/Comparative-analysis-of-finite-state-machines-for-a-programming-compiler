class Token:
    def __init__(self, type="", name="", id=0):
        self.type = type
        self.name = name
        self.id = id

class SymbolTableEntry:
    def __init__(self, type="", name=""):
        self.type = type
        self.name = name

sourcecode = ""
lexbeg = 0
fwdptr = 0
state = 0
symbolcount = 0
symbol_table = []
newtoken = Token()
lineno = 1
stack = []  # Stack for braces matching


def indexof(subString, fromIndex, MainString):
    idx = MainString.find(subString, fromIndex)
    return idx if idx != -1 else -1

def subString(MainString, fromIndex, toIndex):
    if fromIndex < 0 or fromIndex >= len(MainString) or toIndex < fromIndex or toIndex >= len(MainString):
        print("\nError in args: subString fn")
        return None
    return MainString[fromIndex:toIndex+1]

def nextchar():
    global fwdptr
    if fwdptr >= len(sourcecode):
        return '\0'  # End of file
    fwdptr += 1
    return sourcecode[fwdptr-1]

def retract(n):
    global fwdptr
    fwdptr -= n

def fail(msg):
    print(msg)
    return -1

def installid(string):
    global symbolcount, symbol_table
    for i in range(symbolcount):
        if symbol_table[i].name == string:
            return i
    symbol_table.append(SymbolTableEntry("identifier", string))
    symbolcount += 1
    return symbolcount - 1

def isSymbol(c):
    syms = ['.', '<', '>', ',', '{', '}', '(', ')', '#', ';', '=', '+', '*', '>=']
    if c in syms:
        return syms.index(c) + 41
    return 0

# Pushdown Automaton Transition Function
def transition(state, symbol, stack):
    global lexbeg, fwdptr, lineno, newtoken
    match state:
        case 0:  # Initial state
            c = nextchar()
            if c in [' ', '\t', '\n']:
                if c == '\n':
                    lineno += 1
                    print(f"\nline {lineno}: ")
                return 0, stack  # Stay in the same state
            elif c == '{':
                stack.append('{')
                newtoken = Token("symbol", "{", isSymbol(c))
                print_token()
                return 0, stack
            elif c == '}':
                if stack and stack[-1] == '{':
                    stack.pop()
                    newtoken = Token("symbol", "}", isSymbol(c))
                else:
                    print("Error: Unmatched '}' at line", lineno)
                print_token()
                return 0, stack
            elif c.isalpha():  # Start of an identifier or keyword
                lexbeg = fwdptr - 1
                return 10, stack
            elif c.isdigit():  # Start of a numeric constant
                lexbeg = fwdptr - 1
                return 22, stack
            elif c == '=':
                lexbeg = fwdptr - 1
                return 30, stack
            elif c in "+*<>":
                lexbeg = fwdptr - 1
                return 40, stack
            elif isSymbol(c):  # Reserved symbols
                newtoken = Token("Reserved Symbol", c, isSymbol(c))
                print_token()
                return 0, stack
            elif c == '\0':  # End of input
                if stack:
                    print("Error: Unmatched symbols in stack:", stack)
                return -1, stack
            else:
                print(f"Unknown character: '{c}' at line {lineno}")
                return -1, stack
        case 10:  # Reading an identifier or keyword
            c = nextchar()
            if c.isalnum():  # Continue reading
                return 10, stack
            else:  # End of identifier/keyword
                retract(1)
                token_str = subString(sourcecode, lexbeg, fwdptr - 1)
                if token_str in [entry.name for entry in symbol_table if entry.type == "keyword"]:
                    newtoken = Token("keyword", token_str, installid(token_str))
                else:
                    newtoken = Token("identifier", token_str, installid(token_str))
                print_token()
                return 0, stack
        case 22:  # Reading a numeric constant
            c = nextchar()
            if c.isdigit():  # Continue reading
                return 22, stack
            else:  # End of numeric constant
                retract(1)
                token_str = subString(sourcecode, lexbeg, fwdptr - 1)
                newtoken = Token("Numeric constant", token_str, installid("NC"))
                print_token()
                return 0, stack
        case 30:  # Assignment operator
            c = nextchar()
            if c == '=':  # Comparison operator
                newtoken = Token("arop", "EQ", isSymbol("=="))
            else:
                retract(1)
                newtoken = Token("arop", "ASSIGN", isSymbol("="))
            print_token()
            return 0, stack
        case 40:  # Arithmetic operators
            c = nextchar()
            if c == '>':  # Greater than or equal operator
                newtoken = Token("arop", "GE", isSymbol(">="))
            else:
                retract(1)
                op_map = {'+': "PLUS", '*': "MUL", '<': "LT", '>': "GT"}
                newtoken = Token("arop", op_map.get(sourcecode[lexbeg], ""), isSymbol(sourcecode[lexbeg]))
            print_token()
            return 0, stack
        case _:
            print(f"Unhandled state: {state}")
            return -1, stack

def print_token():
    print(f"type: {newtoken.type}, name: {newtoken.name}, id= {newtoken.id}")

# Keywords and Symbols Registration
def regkeywords():
    global symbolcount, symbol_table
    keywords = ["do", "while", "main", "for", "include", "if", "else", "break", "continue", "int", "char", "float", "double", "void", "return", "switch", "case"]
    for word in keywords:
        symbol_table.append(SymbolTableEntry("keyword", word))
    symbol_table.append(SymbolTableEntry("Numeric Constant", "NC"))
    symbolcount = len(symbol_table)

# Main Function
def main():
    global sourcecode, lexbeg, fwdptr, state, lineno, stack

    try:
        with open('test_program.c', 'r') as input_file:
            sourcecode = input_file.read()
    except FileNotFoundError:
        print("Error: Input file 'test_program.c' not found.")
        return

    regkeywords()

    print(f"line {lineno}: ")
    while state != -1:
        state, stack = transition(state, '', stack)

    print("\nSymbol Table:\n")
    for i, entry in enumerate(symbol_table):
        print(f"Type: {entry.type}\tName: {entry.name}\tid= {i}")


if __name__ == "__main__":
    main()
