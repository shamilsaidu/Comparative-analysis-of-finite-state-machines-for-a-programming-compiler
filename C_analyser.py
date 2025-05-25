import re

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

def getType(tok):
    for i in range(symbolcount):
        if symbol_table[i].name == tok:
            return Token(symbol_table[i].type, symbol_table[i].name, i)
    return Token()

def isSymbol(c):
    syms = ['.', '<', '>', ',', '{', '}', '(', ')', '#', ';']
    if c in syms:
        return syms.index(c) + 41
    return 0


def nextToken():
    global state, lexbeg, fwdptr, lineno, sourcecode, newtoken
    state = 0
    c = ''
    temptok = ""
    
    while fwdptr < len(sourcecode) and state != -1:
        match state:
            case 0:
                c = nextchar()
                if c in [' ', '\t', '\n']:
                    state = 0
                    lexbeg += 1
                    if c == '\n':
                        lineno += 1
                        print(f"\nline {lineno}: ")
                    if c == '\0':
                        state = -1
                elif c == '<':
                    state = 1
                elif c == '>':
                    state = 5
                elif c == '=':
                    state = 8
                elif c.isalpha():
                    state = 10
                elif c.isdigit():
                    state = 22
                elif isSymbol(c):
                    state = 24
                elif c == '+':
                    state = 12
                elif c == '-':
                    state = 15
                elif c == '*':
                    state = 18
                elif c == '/':
                    state = 19
                elif c == '%':
                    state = 20
                else:
                    state = fail("unknown symbol encountered")
            
            case 1:
                c = nextchar()
                if c == '=':
                    state = 2
                elif c == '>':
                    state = 3
                else:
                    state = 4

            case 2:
                newtoken = Token("relop", "LE", 17)
                lexbeg = fwdptr
                return newtoken

            case 3:
                newtoken = Token("relop", "NE", 18)
                lexbeg = fwdptr
                return newtoken

            case 4:
                retract(1)
                newtoken = Token("relop", "LT", 19)
                lexbeg = fwdptr
                return newtoken

            case 5:
                c = nextchar()
                if c == '=':
                    state = 6
                else:
                    state = 7

            case 6:
                newtoken = Token("relop", "GE", 20)
                lexbeg = fwdptr
                return newtoken

            case 7:
                retract(1)
                newtoken = Token("relop", "GT", 21)
                lexbeg = fwdptr
                return newtoken

            case 8:
                c = nextchar()
                if c == '=':
                    state = 9
                else:
                    state = 21

            case 9:
                newtoken = Token("relop", "EQ", 22)
                lexbeg = fwdptr
                return newtoken

            case 10:
                c = nextchar()
                if c.isalpha() or c.isdigit():
                    state = 10
                else:
                    state = 11

            case 11:
                retract(1)
                temptok = subString(sourcecode, lexbeg, fwdptr-1)
                newtoken.id = installid(temptok)
                newtoken = getType(temptok)
                lexbeg = fwdptr
                return newtoken

            case 12:
                c = nextchar()
                if c == '+':
                    state = 13
                else:
                    state = 14

            case 13:
                newtoken = Token("arop", "INC", 23)
                lexbeg = fwdptr
                return newtoken

            case 14:
                retract(1)
                newtoken = Token("arop", "PLU", 24)
                lexbeg = fwdptr
                return newtoken

            case 15:
                c = nextchar()
                if c == '-':
                    state = 16
                else:
                    state = 17

            case 16:
                newtoken = Token("arop", "DEC", 25)
                lexbeg = fwdptr
                return newtoken

            case 17:
                retract(1)
                newtoken = Token("arop", "MIN", 26)
                lexbeg = fwdptr
                return newtoken

            case 18:
                newtoken = Token("arop", "MUL", 27)
                lexbeg = fwdptr
                return newtoken

            case 19:
                newtoken = Token("arop", "DIV", 28)
                lexbeg = fwdptr
                return newtoken

            case 20:
                newtoken = Token("arop", "MOD", 29)
                lexbeg = fwdptr
                return newtoken

            case 21:
                retract(1)
                newtoken = Token("arop", "ASSIGN", 30)
                lexbeg = fwdptr
                return newtoken

            case 22:
                c = nextchar()
                if c.isdigit():
                    state = 22
                else:
                    state = 23

            case 23:
                retract(1)
                newtoken = Token("Numeric constant", subString(sourcecode, lexbeg, fwdptr-1), 41)
                lexbeg = fwdptr
                return newtoken

            case 24:
                newtoken = Token("Reserved Symbol", subString(sourcecode, lexbeg, fwdptr-1), isSymbol(c))
                lexbeg = fwdptr
                return newtoken

# Keywords
def regkeywords():
    global symbolcount, symbol_table
    keywords = ["do", "while", "main", "for", "include", "if", "else", "break", "continue", "int", "char", "float", "double", "void", "return", "switch", "case"]
    relop = ["LE", "NE", "LT", "GE", "GT", "EQ"]
    arop = ["INC", "PLU", "DEC", "MIN", "MUL", "DIV", "MOD", "ASSIGN"]
    syms = ['.', '<', '>', ',', '{', '}', '(', ')', '#', ';']

    for i, word in enumerate(keywords):
        symbol_table.append(SymbolTableEntry("keyword", word))
    
    for i, op in enumerate(relop, start=17):
        symbol_table.append(SymbolTableEntry("relop", op))

    for i, op in enumerate(arop, start=23):
        symbol_table.append(SymbolTableEntry("arop", op))

    for i, sym in enumerate(syms, start=31):
        symbol_table.append(SymbolTableEntry("Reserved Symbol", sym))

    symbol_table.append(SymbolTableEntry("Numeric Constant", "NC"))
    symbolcount = 42



def main():
    global sourcecode, lexbeg, fwdptr, state, lineno

    try:
        with open('test_program.c', 'r') as input_file:
            sourcecode = input_file.read()
    except FileNotFoundError:
        print("Error: Input file 'test_program.c' not found.")
        return

    regkeywords()

    print(f"line {lineno}: ")
    nextToken()

    while state != -1:
        print(f"type: {newtoken.type}, name: {newtoken.name}, id= {newtoken.id}")
        nextToken()
        if lexbeg >= len(sourcecode) or fwdptr >= len(sourcecode):
            state = -1

    print("\nSymbol Table:\n")
    for i in range(symbolcount):
        print(f"Type: {symbol_table[i].type}\tName: {symbol_table[i].name}\tid= {i}")


if __name__ == "__main__":
    main()

