# Import
import re
import numpy as np
import string

# Token types based on the implementation scope
TT_kw = 'Keyword'
TT_lit = 'Literal'
TT_id ='Identifier'
TT_sepr = 'Seperator'
TT_op = 'Operator'
# Operands
TT_float_op = 'Float operand'
TT_int_op = 'Integer operand'

# Token patterns
KEYWORDS = {"if", "else", "while", "for", "return", "int", "float", "char", "in", "class", "def"}
OPERATORS = {'+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>='}
PUNCTUATIONS = {';', ',', '(', ')', '{', '}'}

class Token:
    # Value = None because operators are tokens too and they don't have values
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
    # Representation of a Token object when printed/checked
    def __repr__(self):
        if self.value:
            return f'{self.name} : {self.value}'
        else:
            return f'{self.name}'
        
class Lexer:
    def __init__(self, text):
        self.text = text

    def gen_tokens(self):
        tokens = []
        # Split statement into lexemes based on whitespaces
        # then store in a list
        lexemes = self.text.strip().split()

        for lexeme in lexemes:
            if self.is_func_call(lexeme): 
                match = self.is_func_call(lexeme)
                if match:
                    # Returns sub groups of a regex as a tuple
                    # because match.groups() returns a tuple, 
                    # and Python allows tuple unpacking. 
                    # That means if match.groups() returns 
                    # something like ('add', '42'), Python 
                    # automatically assigns:
                    ### 'add' → func_name
                    ### '42' → params

                    func_name, params = match.groups()
                    # function identifier
                    tokens.append(Token(TT_id, func_name))
                    # function stating punctuator
                    tokens.append(Token(TT_sepr, '('))

                    # Simple parameter check
                    if params.startswith('"') and params.endswith('"'):
                        tokens.append(Token(TT_lit, params.strip('"')))
                    elif params.isdigit():
                        tokens.append(Token(TT_int_op, int(params)))
                    elif self.is_float(params):
                        tokens.append(Token(TT_float_op, float(params)))
                    elif self.is_identifier(params):
                        tokens.append(Token(TT_id, params))
                    else:
                        pass  # Reserved for error handler
                # function closing punctuator
                tokens.append(Token(TT_sepr, ')'))
            elif lexeme in KEYWORDS:
                tokens.append(Token(TT_kw, lexeme))
            elif self.is_identifier(lexeme):
                tokens.append(Token(TT_id, lexeme))
            elif lexeme in OPERATORS:
                tokens.append(Token(TT_op, lexeme))
            elif lexeme in PUNCTUATIONS:
                tokens.append(Token(TT_sepr, lexeme))
            elif lexeme.isdigit():
                tokens.append(Token(TT_int_op, int(lexeme)))
            elif self.is_float(lexeme):
                tokens.append(Token(TT_float_op, float(lexeme)))
            elif lexeme.startswith('"') and lexeme.endswith('"'):
                tokens.append(Token(TT_lit, lexeme.strip('"')))
            else:
                # Reserved for error handler
                pass

        return tokens

    # Explicit token pattern definitions 
    def is_func_call(self, lexeme):
        # Return match object if lexeme is a function call
        return re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\((.*)\)$', lexeme)
    
    def is_float(self, num):
        # We use exception handling here as a 
        # fail-safe for when the user enters 
        # letters instead
        try:
            float(num)
            return '.' in num
        except ValueError:
            return False

    def is_integer(self, num): 
        try:
            int(num)
            return True
        except Exception:
            return False

    def is_identifier(self, s):
        # Identifier token pattern
        # Start with a letter (A–Z or a–z) or underscore _
        # Followed by letters, digits (0–9), or underscores
        return re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', s) is not None
        # The above depicts usage of RegEx to match the pattern

class Error(Lexer):
    error_type = ""

    MAX_ID_LENGTH = 30
    # Using int as 2 bytes
    MAX_INT = 32767
    MIN_INT = -32768
    # Using float as 4 bytes -- Can work for both -ves and +ves
    # Actual usable float32 range: −3.4028235e+38 to +3.4028235e+38 based on IEEE Standard
    MAX_FLOAT = np.finfo(np.float32).max   # Largest float = 3.4028235e+38
    MIN_FLOAT = -MAX_FLOAT  # Smallest float = -3.4028235e+38

    def __init__(self, lexeme_with_error):
        self.error = lexeme_with_error
    def detect(self, error_substring):
        pass
    def report(self):
        pass
    def recover(self):
        # Panic mode
        # This will kick in when multiple statements
        # are written in one line seperated by semicolon
        
        # Phrase level
        # Fix misspellings in keywords

        pass
    # All supported error types
    def __is_id_too_long(self, error): 
        state = False
        if self.is_identifier(error) and len(error) >= self.MAX_ID_LENGTH: 
            state = True
        return state
    def __is_num_exceeding_length(self, error):
        is_float = self.is_float(error)
        is_int = self.is_integer(error)
        is_num = is_float or is_int

        if is_num:
            # float
            if is_float:
                num = float(error)
                if num < self.MIN_FLOAT or num > self.MAX_FLOAT:
                    return True
            # int
            elif is_int:
                num = int(error)
                if num < self.MIN_INT or num > self.MAX_INT:
                    return True   
        return False

    def is_num_ill_formed(self, error):
        # To check if special characters are in the number
        invalid_chars = string.ascii_letters + string.punctuation.replace('.', '') + string.whitespace
        # To check if there are two dps in the number
        count_of_dps = 0

        for char in error:
            if char == '.':
                count_of_dps += 1
            if char in invalid_chars or count_of_dps == 2:
                return True
        return False
    def __is_string_ill_formed(self):
        pass

#######################################################
##### Error Handler Code
#######################################################

# statement = ""
# while(True):
#     statement = input('Code >>: ')
#     if statement == "exit": break
#     lexer = Lexer(statement)
#     tokens = lexer.gen_tokens()
#     print(f'{tokens} \n')

# print("\nCode terminated...\n")
