import clang.cindex
import clang.enumerations
import csv
import os

# set the config
# library_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'native')
# clang.cindex.Config.set_library_path(library_path)

class Tokenizer:
    # creates the object, does the inital parse
    def __init__(self, path=None, c_str=None):
        if not path and not c_str:
            raise Exception("Requires atleast one argument among path or c_str")
        self.index = clang.cindex.Index.create()
        if path:
            self.tu = self.index.parse(path)
            self.path = self.extract_path(path)
        if c_str:
            self.tu = clang.cindex.Index.create().parse('temp.c', args=[], unsaved_files=[('temp.c', c_str)])
            self.path = None
        
    # To output for split_functions, must have same path up to last two folders
    def extract_path(self, path):
        return "".join(path.split("/")[:-2])

    # does futher processing on a literal token  
    def process_literal(self, literal):
        cursor_kind = clang.cindex.CursorKind
        kind = literal.cursor.kind

        return list(literal.spelling)
    
    # filters out unwanted punctuation    
    def process_puntuation(self, punctuation):
        spelling = punctuation.spelling
        return [spelling]
    
    # further processes and identifier token    
    def process_ident(self, ident, functions, variables):
        # are we a "special" ident?
        # if ident.spelling in ["std", "cout", "cin", "vector", "pair", "string", "NULL", "size_t", "main"]:
        if ident.spelling in ["continue", "unsigned", "default", "typedef", "define", "double", "extern", "signed", "sizeof", "static", "struct", "switch", "return", "break", "const", "float", "short", "union", "while", "else", "enum", "goto", "long", "main", "void", "for", "int", "do", "if"]:
            return [ident.spelling]

        if ident.cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL or ident.cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
            if ident.spelling not in functions:
                functions.append(ident.spelling)
                return [f"function{functions.index(ident.spelling)}"]
            else:
                return [f"function{functions.index(ident.spelling)}"]
        if ident.cursor.kind == clang.cindex.CursorKind.VAR_DECL or ident.cursor.kind == clang.cindex.CursorKind.PARM_DECL:
            if ident.spelling not in variables:
                variables.append(ident.spelling)
                return [f"variable{variables.index(ident.spelling)}"]
            else:
                return [f"variable{variables.index(ident.spelling)}"]
        if ident.cursor.kind == clang.cindex.CursorKind.DECL_REF_EXPR or ident.cursor.kind == clang.cindex.CursorKind.COMPOUND_STMT:
            if ident.spelling in variables:
                return [f"variable{variables.index(ident.spelling)}"]
            elif ident.spelling in functions:
                return [f"function{functions.index(ident.spelling)}"]
            else:
                functions.append(ident.spelling)
                return [f"function{functions.index(ident.spelling)}"]
                # raise Exception("DECL_REF_EXPR Error")
        print(ident.cursor.kind, ident.spelling)
        return list(ident.spelling)
    
    # tokenizes the contents of a specific cursor
    def full_tokenize_cursor(self, cursor):
        tokens = cursor.get_tokens()
        
        # return final tokens as a list
        result = []
        functions = []
        variables = []

        for token in tokens:
            if token.kind.name == "COMMENT":
                # ignore all comments
                continue
    
            if token.kind.name == "PUNCTUATION":
                punct_or_none = self.process_puntuation(token)
                
                # add only if not ignored
                if punct_or_none != None:
                    result += punct_or_none
                    
                continue
    
            if token.kind.name == "LITERAL":
                result += self.process_literal(token)
                continue
    
            if token.kind.name == "IDENTIFIER":
                # result += ["IDENT"]
                result += self.process_ident(token, functions, variables)
                continue
    
            if token.kind.name == "KEYWORD":
                result += [token.spelling]

        tokenlist = ["", *[f"variable{x}" for x in range(20)], *[f"function{x}" for x in range(30)],  "continue", "unsigned", "default", "typedef", "define", "double", "extern", "signed", "sizeof", "static", "struct", "switch", "return", "break", "const", "float", "short", "union", "while", "auto", "case", "char", "else", "enum", "goto", "long", "main", "void", "for", "int", "do", "if", " ", "!", "?", "_", "\"", "#", "$", "%", "&", "’", "(", ")", "*", "+", ",", "-", ".", "/", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ":", ";", "<", "=", ">", "@", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "[", "\\", "]", "⌃", "‘", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "{", "|", "}", "∼"]
        r = []
        for i in result:
            if i in tokenlist:
                r.append(i)
            else:
                r+=list(i)
        return (r, functions, variables)
    
    # tokenizes the entire document
    def full_tokenize(self):
        cursor = self.tu.cursor
        return self.full_tokenize_cursor(cursor)
    
if __name__ == "__main__":
    # testing function
    import sys
    
    if len(sys.argv) != 2:
        print("please provide a file argument")
        exit(1)
        
    tok = Tokenizer(sys.argv[1]) # path to a C++ file
    results = tok.split_functions(False)
    for res in results:
        print(res[0] + " (" + res[2] + "):")
        print("Tokens: {}".format(res[1]))
        print("")
