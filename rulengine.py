import operator
import json
from typing import Union, Dict

# Define the Node class representing each node in the AST
class Node:
    def __init__(self, node_type: str, left: 'Node' = None, right: 'Node' = None, value: Union[str, int, float] = None):
        self.type = node_type  # "operator" or "operand"
        self.left = left  # Left child (Node)
        self.right = right  # Right child (Node)
        self.value = value  # Operand value, if it's a leaf node

    def __repr__(self):
        if self.type == "operator":
            return f"({self.left} {self.value} {self.right})"
        else:
            return str(self.value)

# Parse rule strings into AST
class RuleEngine:
    OPERATORS = {
        'AND': operator.and_,
        'OR': operator.or_,
        '>': operator.gt,
        '<': operator.lt,
        
        '=': operator.eq
    }

    def __init__(self):
        self.rules_db = {}  # In-memory database to store rules

    def create_rule(self, rule_string: str) -> Node:
        """Converts a rule string into an AST."""
        tokens = self.tokenize(rule_string)
        ast = self.build_ast(tokens)
        return ast

    def tokenize(self, rule_string: str):
        """Tokenizes the input rule string."""
        return rule_string.replace('(', ' ( ').replace(')', ' ) ').split()

    def build_ast(self, tokens: list):
        """Recursively builds the AST from the list of tokens."""
        if not tokens:
            return None

        token = tokens.pop(0)

        if token == '(':
            left_node = self.build_ast(tokens)
            operator_token = tokens.pop(0)
            right_node = self.build_ast(tokens)
            tokens.pop(0)  # Pop the closing ')'
            return Node(node_type='operator', left=left_node, right=right_node, value=operator_token)

        elif token.isdigit():
            return Node(node_type='operand', value=int(token))
        elif token.startswith("'") and token.endswith("'"):
            return Node(node_type='operand', value=token.strip("'"))
        elif token.isalpha():
            return Node(node_type='operand', value=token)
        else:
            raise ValueError(f"Invalid token: {token}")

    def combine_rules(self, rules: list) -> Node:
        """Combines multiple ASTs into a single AST."""
        if not rules:
            return None

        combined_ast = self.create_rule(rules[0])
        for rule_string in rules[1:]:
            rule_ast = self.create_rule(rule_string)
            combined_ast = Node(node_type='operator', left=combined_ast, right=rule_ast, value='AND')

        return combined_ast

    def evaluate_rule(self, ast: Node, data: Dict) -> bool:
        """Evaluates the AST against the provided data."""
        if ast is None:
            return False

        if ast.type == 'operand':
            if isinstance(ast.value, str) and ast.value in data:
                return data[ast.value]
            return ast.value

        left_result = self.evaluate_rule(ast.left, data)
        right_result = self.evaluate_rule(ast.right, data)

        operator_func = self.OPERATORS.get(ast.value)

        if operator_func:
            return operator_func(left_result, right_result)
        else:
            raise ValueError(f"Unknown operator: {ast.value}")

    def save_rule(self, rule_id: str, rule_string: str, ast: Node):
        """Saves the rule and AST to an in-memory database (or persistent storage)."""
        self.rules_db[rule_id] = {
            'rule_string': rule_string,
            'ast': ast
        }

    def get_rule(self, rule_id: str):
        """Retrieves the rule and AST from the database."""
        return self.rules_db.get(rule_id)


# Example usage
rule_engine = RuleEngine()

# Creating individual rules and ASTs
rule1_string = "((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)"
rule2_string = "((age > 30 AND department = 'Marketing')) AND (salary > 20000 OR experience > 5)"

rule1_ast = rule_engine.create_rule(rule1_string)
rule2_ast = rule_engine.create_rule(rule2_string)

print("AST for Rule 1:", rule1_ast)
print("AST for Rule 2:", rule2_ast)

# Combine rules
combined_ast = rule_engine.combine_rules([rule1_string, rule2_string])
print("Combined AST:", combined_ast)

# Sample data for evaluation
data = {"age": 35, "department": "Sales", "salary": 60000, "experience": 3}

# Evaluating the combined rule
is_eligible = rule_engine.evaluate_rule(combined_ast, data)
print(f"Is the user eligible? {is_eligible}")

# Saving rules to the database
rule_engine.save_rule('rule1', rule1_string, rule1_ast)
rule_engine.save_rule('rule2', rule2_string, rule2_ast)

# Retrieving and evaluating a saved rule
saved_rule = rule_engine.get_rule('rule1')
print("Saved rule AST:", saved_rule['ast'])
