from typing import Any


class LiONException(RuntimeError):
    def __init__(self, msg, node: dict[str, Any] = None):
        self.msg = msg
        self.node = node

    def get_node(self):
        return self.node


class NodeThrownError(LiONException):
    pass


class ParsingError(LiONException):
    pass


class LexingError(LiONException):
    pass


class BracketMismatch(LexingError):
    pass


class BracketNeverClosed(BracketMismatch):
    pass


class EmptyBracket(LexingError):
    pass


class EmptyMask(EmptyBracket):
    pass


class StringNeverClosed(LexingError):
    pass


class PairMismatch(LexingError):
    pass


class IsNotANode(ParsingError):
    pass


class NodeNotFound(IsNotANode):
    pass


class IsANode(ParsingError):
    pass


class NodeIsNotAVariable(ParsingError):
    pass


class NodeIsNotAModule(ParsingError):
    pass


class NodeIsNotACommand(ParsingError):
    pass


class NodeIsProtected(ParsingError):
    pass


class NodeIsFinal(ParsingError):
    pass


class NodeIsGlobal(ParsingError):
    pass


class NodeIsNotAKeyword(ParsingError):
    pass


class MaskSyntaxError(LexingError):
    pass


class InvalidExpression(MaskSyntaxError):
    pass


class InvalidToken(MaskSyntaxError):
    pass


class InvalidContext(ParsingError):
    pass


class NotAvailableInStack(ParsingError):
    pass


class IncompleteCallError(ParsingError):
    pass


class DateError(ParsingError):
    pass


class InvalidDateUnitError(DateError):
    pass


class DMSError(LiONException):
    pass


class InformalDMSRegistryError(DMSError):
    pass


class UndefinedClassError(ParsingError):
    pass


class ClassWithoutMethod(ParsingError):
    pass


class ClassMismatch(ParsingError):
    pass


class ArgumentBindingMismatchError(ParsingError):
    pass


class FlippingError(ParsingError):
    pass


class InvalidRegistryDomainError(ParsingError):
    pass


class InvalidRegistryError(ParsingError):
    pass
