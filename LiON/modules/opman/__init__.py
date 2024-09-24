import LiON.parser
from LiON.lang.const import *
from typing import Hashable, Any


class OperatorManager:
    def __init__(self, tree: LiON.parser.TreeManager):
        self.tree = tree

        self.exec_tree = {
            DEFAULT_OPERATOR: {
                1: self.exec_def_type1,
                2: self.exec_def_type2
            },
            OPERATOR: {
                1: self.exec_type1,
                2: self.exec_type2
            }
        }

    def get_operators(self) -> dict[str, Any]:
        return self.tree.get_registry_domain(REGISTRY_OPERATOR)

    def get(self, name: str):
        return self.tree.query_registry(REGISTRY_OPERATOR, name)

    @staticmethod
    def get_operator_type(operator: dict[str, Any]) -> int:
        return operator[TYPE_ATTRIBUTE]

    @staticmethod
    def get_operator_precedence(operator: dict[str, Any]):
        return operator[PRECEDENCE_ATTRIBUTE]

    @staticmethod
    def exec_def_type1(operator: dict[str, Any], operand):
        return operator[LAMBDA_ATTRIBUTE](operand)

    @staticmethod
    def exec_def_type2(operator: dict[str, Any], operand1, operand2):
        return operator[LAMBDA_ATTRIBUTE](operand1, operand2)

    def exec_type1(self, operator: dict[str, Any], operand):
        output = self.tree.exec_function(operator[LAMBDA_ATTRIBUTE], (operand,))
        return output

    def exec_type2(self, operator: dict[str, Any], operand1, operand2):
        output = self.tree.exec_function(operator[LAMBDA_ATTRIBUTE], (operand1, operand2))
        return output

    def exec(self, operator: dict[str, Any], args):
        return self.exec_tree[operator[CLASS_ATTRIBUTE]][operator[TYPE_ATTRIBUTE]](operator, *args)

    def is_operator(self, char):
        if isinstance(char, Hashable):
            return char in self.get_operators()
        return False

    def shunting_yard(self, expression: list | tuple):
        output = []
        operator_stack = []

        for token in expression:
            if isinstance(token, list):
                output.append(self.shunting_yard(token))
            elif self.is_operator(token):
                operator = self.get(token)
                precedence = self.get_operator_precedence(operator)

                while operator_stack and precedence <= self.get_operator_precedence(self.get(operator_stack[-1])):
                    output.append(operator_stack.pop())

                operator_stack.append(token)
            else:
                output.append(token)

        while operator_stack:
            output.append(operator_stack.pop())

        return output

    def parse_sorted(self, expression: list | tuple):
        stack = []

        for token in expression:
            # check if it is an operator
            if self.is_operator(token):
                operator: dict[str, Any] = self.get(token)

                # check if dual
                op_type = self.get_operator_type(operator)
                operand_1 = stack.pop()
                if op_type == 1:
                    stack.append(self.exec(operator, (operand_1,)))
                    continue

                operand_2 = stack.pop()
                stack.append(self.exec(operator, (operand_2, operand_1)))
                continue

            stack.append(token)

        return stack[-1]


