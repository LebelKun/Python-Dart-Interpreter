import re

# Token types for Dart-like code
TOKEN_TYPES = {
    'VAR': r'var',
    'PRINT': r'print',
    'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*',
    'EQUALS': r'=',
    'COMMA': r',',
    'SEMICOLON': r';',
    'NUMBER': r'\d+',
    'WHITESPACE': r'\s+',
    'LPAREN': r'\(',
    'RPAREN': r'\)',
    'PLUS': r'\+',
    'MINUS': r'-',
    'TIMES': r'\*',
    'DIVIDE': r'/',
}

# Token class representing a token in the code
class Token:
    def __init__(self, type_, value):
        """Initialize a token with its type and value.
        
        Args:
            type_ (str): The type of the token.
            value (str): The value of the token.
        """
        self.type = type_
        self.value = value

    def __repr__(self):
        """Return a string representation of the token."""
        return f'Token({self.type}, {self.value})'

# Lexer function that converts code into tokens
def lex(code):
    """Lexical analyzer that converts source code into a list of tokens.
    
    Args:
        code (str): The source code to be tokenized.
        
    Returns:
        list[Token]: A list of tokens extracted from the code.
    """
    tokens = []
    # Create a regex pattern for all token types
    token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES.items())
    for match in re.finditer(token_regex, code):
        type_ = match.lastgroup
        value = match.group(type_)
        if type_ == 'WHITESPACE':
            continue  # Skip whitespace tokens
        tokens.append(Token(type_, value))
    return tokens

# AST Node classes to represent different types of statements
class VariableNode:
    def __init__(self, name, value):
        """Initialize a variable node.
        
        Args:
            name (str): The name of the variable.
            value: The value of the variable (expression to evaluate).
        """
        self.name = name
        self.value = value

class PrintNode:
    def __init__(self, expression):
        """Initialize a print node.
        
        Args:
            expression: The expression to print (can be a variable or calculation).
        """
        self.expression = expression

class BinaryOperationNode:
    def __init__(self, left, operator, right):
        """Initialize a binary operation node.
        
        Args:
            left: The left operand (can be a number or a variable).
            operator (str): The operator ('+', '-', '*', '/').
            right: The right operand (can be a number or a variable).
        """
        self.left = left
        self.operator = operator
        self.right = right

# Parser function that converts tokens into an Abstract Syntax Tree (AST)
def parse(tokens):
    """Parse tokens into a list of statements (AST).
    
    Args:
        tokens (list[Token]): A list of tokens to parse.
        
    Returns:
        list: A list of statement nodes (VariableNode or PrintNode).
        
    Raises:
        SyntaxError: If the code has syntax errors.
    """
    statements = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type == 'VAR':
            i += 1  # Skip 'var'
            if i >= len(tokens) or tokens[i].type != 'IDENTIFIER':
                raise SyntaxError(f'Expected identifier after "var" at position {i}.')
            name = tokens[i].value
            i += 1  # Skip identifier
            if i >= len(tokens) or tokens[i].type != 'EQUALS':
                raise SyntaxError(f'Expected "=" after "{name}" at position {i}.')
            i += 1  # Skip '='
            value = parse_expression(tokens[i:])  # Parse the expression on the right side of '='
            statements.append(VariableNode(name, value))  # Create a variable node
            while i < len(tokens) and tokens[i].type != 'SEMICOLON':
                i += 1  # Skip until semicolon
            i += 1  # Skip ';'
        elif token.type == 'PRINT':
            i += 1  # Skip 'print'
            if i >= len(tokens) or tokens[i].type != 'LPAREN':
                raise SyntaxError(f'Expected "(" after "print" at position {i}.')
            i += 1  # Skip '('
            expression = parse_expression(tokens[i:])  # Parse the expression inside the parentheses
            statements.append(PrintNode(expression))  # Create a print node
            while i < len(tokens) and tokens[i].type != 'RPAREN':
                i += 1  # Skip until ')'
            i += 1  # Skip ')'
            while i < len(tokens) and tokens[i].type != 'SEMICOLON':
                i += 1  # Skip until semicolon
            i += 1  # Skip ';'
        else:
            raise SyntaxError(f'Unexpected token: {token} at position {i}.')
    return statements

# Parse expressions with binary operations (like addition)
def parse_expression(tokens):
    """Parse an expression into a binary operation or a number/identifier.
    
    Args:
        tokens (list[Token]): A list of tokens representing an expression.
        
    Returns:
        The parsed expression (int or BinaryOperationNode).
        
    Raises:
        SyntaxError: If the expression has syntax errors.
    """
    if tokens[0].type == 'NUMBER':
        left = int(tokens[0].value)  # Parse number
        i = 1
    elif tokens[0].type == 'IDENTIFIER':
        left = tokens[0].value  # Parse identifier
        i = 1
    else:
        raise SyntaxError(f'Expected number or identifier at position 0.')
    
    while i < len(tokens) and tokens[i].type in {'PLUS', 'MINUS', 'TIMES', 'DIVIDE'}:
        operator = tokens[i].value  # Get operator
        i += 1
        if i >= len(tokens) or tokens[i].type not in {'NUMBER', 'IDENTIFIER'}:
            raise SyntaxError(f'Expected number or identifier after operator "{operator}" at position {i}.')
        right = int(tokens[i].value) if tokens[i].type == 'NUMBER' else tokens[i].value  # Parse right operand
        left = BinaryOperationNode(left, operator, right)  # Create binary operation node
        i += 1
    return left

# Evaluator class for managing variables and evaluating expressions
class Environment:
    def __init__(self):
        """Initialize an environment to store variables."""
        self.variables = {}

    def set(self, name, value):
        """Set the value of a variable.
        
        Args:
            name (str): The name of the variable.
            value: The value to assign to the variable.
        """
        self.variables[name] = value

    def get(self, name):
        """Get the value of a variable.
        
        Args:
            name (str): The name of the variable.
            
        Returns:
            The value of the variable, or None if not found.
        """
        return self.variables.get(name, None)

    def evaluate_expression(self, expression):
        """Evaluate an expression (number, variable, or binary operation).
        
        Args:
            expression: The expression to evaluate.
            
        Returns:
            The result of the evaluation.
            
        Raises:
            RuntimeError: If there's an unknown expression type or division by zero.
        """
        if isinstance(expression, int):
            return expression  # Return number directly
        elif isinstance(expression, str):  # Variable reference
            return self.get(expression)  # Return variable value
        elif isinstance(expression, BinaryOperationNode):
            left = self.evaluate_expression(expression.left)  # Evaluate left operand
            right = self.evaluate_expression(expression.right)  # Evaluate right operand
            if expression.operator == '+':
                return left + right
            elif expression.operator == '-':
                return left - right
            elif expression.operator == '*':
                return left * right
            elif expression.operator == '/':
                if right == 0:
                    raise RuntimeError("Division by zero.")  # Handle division by zero
                return left / right
            else:
                raise SyntaxError(f"Unknown operator: {expression.operator}")
        else:
            raise RuntimeError(f"Unknown expression type: {type(expression)}")

def evaluate(statements, env):
    """Evaluate a list of statements in a given environment.
    
    Args:
        statements (list): A list of statement nodes (VariableNode or PrintNode).
        env (Environment): The environment containing variables.
        
    Raises:
        RuntimeError: If there's an unknown statement type.
    """
    for statement in statements:
        if isinstance(statement, VariableNode):
            value = env.evaluate_expression(statement.value)  # Evaluate variable's value
            env.set(statement.name, value)  # Set variable in environment
        elif isinstance(statement, PrintNode):
            value = env.evaluate_expression(statement.expression)  # Evaluate expression to print
            print(f'{statement.expression}: {value}')  # Output the result
        else:
            raise RuntimeError('Unknown statement type.')

# Main function to run the interpreter
def main():
    """Main function to execute the Dart-like interpreter."""
    code = """
    var flour = 2;
    var sugar = 1;
    var total = flour + sugar;
    print(total);
    """

    try:
        tokens = lex(code)  # Tokenize the code
        statements = parse(tokens)  # Parse tokens into statements
        env = Environment()  # Create a new environment
        evaluate(statements, env)  # Evaluate statements in the environment
    except (SyntaxError, RuntimeError) as e:
        print(f'Error: {e}')  # Catch and display errors

if __name__ == '__main__':
    main()  # Run the interpreter
