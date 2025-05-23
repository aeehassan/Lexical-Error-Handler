####
# Problems encountered
# 1. Exceeded Recursion call depth error
# ##

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
KEYWORDS = {"if", "else", "while", "for", "return", "int", "float", "char", "class", "def"}
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
                error = Error()
                error.detect(lexeme)
                error.report()
                # Recovers from error with the corrected lexeme as output
                corrected_lexeme = error.recover(lexeme, lexemes)

                if corrected_lexeme == None:
                    pass
                elif corrected_lexeme != None:
                    # This indexes the semicolon token
                    lexeme = lexemes[corrected_lexeme]
                # Phrase level - Deduces its type then adds to list
                elif corrected_lexeme in KEYWORDS:
                    tokens.append(Token(TT_kw, corrected_lexeme))
                elif corrected_lexeme.startswith('"') and corrected_lexeme.endswith('"'):
                    tokens.append(Token(TT_lit, corrected_lexeme.strip('"')))

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
        # The identifier string is a kw if it's one char away from the closest kw
        def is_similar_to_keyword(lexeme, max_distance=1):
            def levenshtein(a, b):
                m, n = len(a), len(b)
                dp = [[0] * (n + 1) for _ in range(m + 1)]
                for i in range(m + 1): dp[i][0] = i
                for j in range(n + 1): dp[0][j] = j
                for i in range(1, m + 1):
                    for j in range(1, n + 1):
                        cost = 0 if a[i - 1] == b[j - 1] else 1
                        dp[i][j] = min(
                            dp[i - 1][j] + 1,      # deletion
                            dp[i][j - 1] + 1,      # insertion
                            dp[i - 1][j - 1] + cost  # substitution
                        )
                return dp[m][n]

            for kw in KEYWORDS:
                if levenshtein(lexeme, kw) <= max_distance:
                    return True
            return False

        def is_id_too_long(error): 
            state = False
            if len(error) >= 15: 
                state = True
            return state

        # Identifier token pattern
        # Start with a letter (A–Z or a–z) or underscore _
        # Followed by letters, digits (0–9), or underscores
        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', s):
            if s in KEYWORDS:
                return False  # Exact match — not an identifier
            if is_similar_to_keyword(s):
                return False  # Too similar — not an identifier
            if is_id_too_long(s):
                return False
            return True
        return False



class Error(Lexer):

    error_type = ""
    MAX_ID_LENGTH = 15
    # Using int as 2 bytes
    MAX_INT = 32767
    MIN_INT = -32768
    # Using float as 4 bytes -- Can work for both -ves and +ves
    # Actual usable float32 range: −3.4028235e+38 to +3.4028235e+38 based on IEEE Standard
    MAX_FLOAT = np.finfo(np.float32).max   # Largest float = 3.4028235e+38
    MIN_FLOAT = -MAX_FLOAT  # Smallest float = -3.4028235e+38

    def __init__(self):
        pass

    def detect(self, error):
        if (self.__is_id_too_long(error)): 
            self.error_type = "Identifier exceeds 15 characters"
        elif (self.__is_num_exceeding_length(error)):
            self.error_type = "Numeric type exceeds defined range"
        elif (self.__is_string_ill_formed(error)):
            self.error_type = "Ill-formed string literal"
        elif (self.__is_num_ill_formed(error)):
            self.error_type = "Ill-formed numeric type"

        return self.error_type

    def report(self):
        print(f'{self.error_type} \n')

    def recover(self, lexeme, lexemes = None):
        # Panic mode recovery
        # Triggered if multiple semicolons are present (multiple statements)
        # and an error type occurs that is not fixable at phrase level
        if self.__is_other_error(lexeme):
            if lexemes.count(';') > 1:
                # Find the first semicolon AFTER the infected lexeme
                start_index = lexemes.index(lexeme)
                for i in range(start_index + 1, len(lexemes)):
                    if lexemes[i] == ';' and i + 1 < len(lexemes):
                        # Return the first semicolon after the lexeme
                        return i
            # If one or no semicolon found after current lexeme, skip recovery
            return None
        # Phrase level
        # Fixes misspellings in keywords and ill-formed string literals
        else:
            # ill-formed string literals
            if (self.__is_string_ill_formed(lexeme)):
                # Determine which quote to use (default to double quote)
                if lexeme[0] == '"' or lexeme[-1] == '"':
                    quote_char = '"'
                elif lexeme[0] == "'" or lexeme[-1] == "'":
                    quote_char = "'"

                # Add opening quote if missing
                if lexeme[0] != quote_char:
                    lexeme = quote_char + lexeme
                # Add closing quote if missing
                if lexeme[-1] != quote_char:
                    lexeme = lexeme + quote_char
            
            # Misspellings in keywords
            elif self.__is_keyword_invalid(lexeme):
                closest = None  # Best match keyword from KEYWORDS
                highest_shared = -1  # Max number of shared characters seen so far
                smallest_distance = float('inf')  # Not used directly but kept for extension

                # Helper: counts how many characters in 'a' also appear in 'b'
                def shared_chars(a, b):
                    # return sum(1 for char in a if char in b) -- Actual code but quite ambiguous
                    return len(set(a) & set(b))

                
                # Find the closest keyword based on Levenshtein-like distance (here: shared characters)
                # Levenshtein distance (also called edit distance) is a way to measure how different 
                # two strings are
                #####
                # Find keyword that shares the most characters with the invalid lexeme
                for kw in KEYWORDS:
                    shared = shared_chars(lexeme, kw)
                    dist = abs(len(kw) - len(lexeme))  # Optional metric (could be useful for fine-tuning)

                    # Update the closest keyword if current one shares more characters
                    if shared > highest_shared:
                        closest = kw
                        highest_shared = shared
                        smallest_distance = dist

                # If a valid close keyword was found, consider fixing the invalid one 
                # The faulty keyword must less than the closest token
                if closest:
                    if len(lexeme) <= len(closest):
                        # If lexeme is shorter or equal, only fix if it shares at least 2 chars
                        if highest_shared >= 2:
                            return closest
                    else:
                        # If lexeme is longer than the keyword, just replace it
                        return closest

            #### One of two outcomes
            # 1. No good match found; return original unchanged 
            # 2. Recovered version
            return lexeme

    # Error type check
    def __is_other_error(self, lexeme):
        return (
            self.__is_id_too_long(lexeme) or
            self.__is_num_exceeding_length(lexeme) or 
            self.__is_num_ill_formed(lexeme)
        )

    # All supported error types    
    def __is_keyword_invalid(self, word):
        return word not in KEYWORDS
    
    def __is_id_too_long(self, error): 
        state = False
        def is_similar_to_keyword(lexeme, max_distance=1):
            def levenshtein(a, b):
                m, n = len(a), len(b)
                dp = [[0] * (n + 1) for _ in range(m + 1)]
                for i in range(m + 1): dp[i][0] = i
                for j in range(n + 1): dp[0][j] = j
                for i in range(1, m + 1):
                    for j in range(1, n + 1):
                        cost = 0 if a[i - 1] == b[j - 1] else 1
                        dp[i][j] = min(
                            dp[i - 1][j] + 1,      # deletion
                            dp[i][j - 1] + 1,      # insertion
                            dp[i - 1][j - 1] + cost  # substitution
                        )
                return dp[m][n]

            for kw in KEYWORDS:
                if levenshtein(lexeme, kw) <= max_distance:
                    return True
            return False

        is_identifier = (re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', error)) and (is_similar_to_keyword(error) == False)

        if is_identifier and len(error) >= self.MAX_ID_LENGTH: 
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

    def __is_num_ill_formed(self, error):
        # Pre-check: if there's no digit at all, it can't be close to a number
        if not any(char.isdigit() for char in error):
            return False
        
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
    
    def __is_string_ill_formed(self, error):
        # The -1 indexing works because sequences
        # support -ve indexing as a way to count
        # from the end
        is_string = (error[0] in '"\'') or (error[-1] in '"\'')

        if is_string:
            # Handle the case when the string is empty 
            # (to avoid index errors)
            if len(error) < 2:
                # Too short to be properly quoted 
                return True
            if (error[0] != error[-1]): 
                return True            
            
        return False

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



# Things to keep track of
error = Error()
print(error.detect("ahsjasjaks_Adjdjdhs_sjbdjsjs_fdkfjdfjdjfbd"))
print(error.detect("1.2.2.323323$"))
print(error.detect("128781728128"))
# Logical error: Can't figure out float
print(error.detect("1.02^2"))
print('\n\n')
