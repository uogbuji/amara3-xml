# amara3.uxml.uxpath.parserules
'''
XPath parsing rules.

Heavy debt to: https://github.com/emory-libraries/eulxml/blob/master/eulxml/xpath/parserules.py
'''

from . import ast
from .lexrules import tokens

precedence = (
    ('left', 'OR_OP'),
    ('left', 'AND_OP'),
    ('left', 'EQUAL_OP'),
    ('left', 'REL_OP'),
    ('left', 'PLUS_OP', 'MINUS_OP'),
    ('left', 'MULT_OP', 'DIV_OP', 'MOD_OP'),
    ('right', 'UMINUS_OP'),
    ('left', 'UNION_OP'),
)

#
# basic expressions
#

def p_expr_boolean(p):
    """
    Expr : Expr OR_OP Expr
         | Expr AND_OP Expr
         | Expr EQUAL_OP Expr
         | Expr REL_OP Expr
         | Expr PLUS_OP Expr
         | Expr MINUS_OP Expr
         | Expr MULT_OP Expr
         | Expr DIV_OP Expr
         | Expr MOD_OP Expr
    """
    p[0] = ast.BinaryExpression(p[1], p[2], p[3])

def p_expr_unary(p):
    """
    Expr : MINUS_OP Expr %prec UMINUS_OP
    """
    p[0] = ast.UnaryExpression(p[1], p[2])

#
# sequence expressions
#

def p_expr_sequence_empty(p):
    """
    Expr : OPEN_PAREN CLOSE_PAREN
    """
    p[0] = ast.Sequence([])

def p_expr_sequence(p):
    """
    Expr : OPEN_PAREN ExprList CLOSE_PAREN
    """
    p[0] = ast.Sequence(p[2])

def p_expr_list_single(p):
    """
    ExprList : Expr
    """
    p[0] = [p[1]]

def p_expr_list_recursive(p):
    """
    ExprList : ExprList COMMA Expr
    """
    p[0] = p[1]
    p[0].append(p[3])

#
# path expressions
#

def p_path_union_expr(p):
    """
    Expr : Expr UNION_OP Expr
    """
    p[0] = ast.BinaryExpression(p[1], p[2], p[3])

def p_path_expr_binary(p):
    """
    Expr : Expr PATH_SEP RelativeLocationPath
         | Expr ABBREV_PATH_SEP RelativeLocationPath
    """
    p[0] = ast.BinaryExpression(p[1], p[2], p[3])

def p_expr_paths_etc(p):
    """
    Expr : RelativeLocationPath
         | AbsoluteLocationPath
         | AbbreviatedAbsoluteLocationPath
         | PredicatedExpression
         | FunctionCall
         | VariableReference
    """
    p[0] = p[1]

def p_expr_literal(p):
    """
    Expr : LITERAL
         | Number
    """
    p[0] = ast.LiteralWrapper(p[1])

#
# paths
#

def p_absolute_location_path_rootonly(p):
    """
    AbsoluteLocationPath : PATH_SEP
    """
    p[0] = ast.AbsolutePath(p[1])

def p_absolute_location_path_subpath(p):
    """
    AbsoluteLocationPath : PATH_SEP RelativeLocationPath
    """
    p[0] = ast.AbsolutePath(p[1], p[2])

def p_abbreviated_absolute_location_path(p):
    """
    AbbreviatedAbsoluteLocationPath : ABBREV_PATH_SEP RelativeLocationPath
    """
    p[0] = ast.AbsolutePath(p[1], p[2])

def p_relative_location_path_simple(p):
    """
    RelativeLocationPath : Step
    """
    p[0] = p[1]

def p_relative_location_path_binary(p):
    """
    RelativeLocationPath : RelativeLocationPath PATH_SEP Step
                         | RelativeLocationPath ABBREV_PATH_SEP Step
    """
    p[0] = ast.BinaryExpression(p[1], p[2], p[3])

#
# path steps
#

def p_step_axis_nodetest(p):
    """
    Step : AxisSpecifier NodeTest
    """
    p[0] = ast.Step(p[1], p[2])

def p_step_nodetest(p):
    """
    Step : NodeTest
    """
    #For MicroXML we can assume child axis
    p[0] = ast.Step('child', p[1])

def p_step_abbrev(p):
    """
    Step : ABBREV_STEP_SELF
         | ABBREV_STEP_PARENT
    """
    p[0] = ast.AbbreviatedStep(p[1])

#
# axis specifier
#

def p_axis_specifier_full(p):
    """
    AxisSpecifier : NAME AXIS_SEP
    """
    #XPath 1.0 axes - namespace
    if p[1] not in ('self', 'attribute', 'ancestor', 'ancestor-or-self', 'attribute', 'child', 'descendant', 'descendant-or-self', 'following', 'following-sibling', 'parent', 'preceding', 'preceding-sibling'):
        raise RuntimeError("Invalid axis name '{0}'".format(p[1]))
    p[0] = p[1]

def p_axis_specifier_abbrev(p):
    """
    AxisSpecifier : ABBREV_AXIS_AT
    """
    p[0] = 'attribute'

#
# node test
#

def p_node_test_name_test(p):
    """
    NodeTest : NameTest
    """
    p[0] = p[1]

def p_node_test_type(p):
    #NodeTest : NODETEXTTEST
    """
    NodeTest : FunctionCall
    """
    # FIXME: Also check no args
    if p[1].name not in ('node', 'text'):
        raise RuntimeError("Invalid node test '{0}'".format(p[1]))
    p[0] = p[1]

#
# name test
#

def p_name_test_star(p):
    """
    NameTest : STAR_OP
    """
    p[0] = ast.NameTest('*')

def p_name_test_name(p):
    """
    NameTest : NAME
    """
    p[0] = ast.NameTest(p[1])

#
# predicated expressions
#

def p_expr_predicates(p):
    """
    PredicatedExpression : Expr PredicateList
    """
    p[0] = ast.PredicatedExpression(p[1], p[2])

#
# predicates
#

def p_predicate_list_single(p):
    """
    PredicateList : Predicate
    """
    p[0] = [p[1]]

def p_predicate_list_recursive(p):
    """
    PredicateList : PredicateList Predicate
    """
    p[0] = p[1]
    p[0].append(p[2])

def p_predicate(p):
    """
    Predicate : OPEN_BRACKET Expr CLOSE_BRACKET
    """
    p[0] = p[2]

#
# variable
#

def p_variable_reference(p):
    """
    VariableReference : DOLLAR NAME
    """
    p[0] = ast.VariableReference(p[2])

#
# number
#

def p_number(p):
    """
    Number : FLOAT
           | INTEGER
    """
    p[0] = p[1]

#
# funcall
#

def p_function_call(p):
    """
    FunctionCall : NAME FormalArguments
    """
    #Hacking around the ambiguity between node type test & function call
    if p[1] in ('node', 'text'):
        p[0] = ast.NodeTypeTest(p[1])
    else:
        p[0] = ast.FunctionCall(p[1], p[2])

def p_formal_arguments_empty(p):
    """
    FormalArguments : OPEN_PAREN CLOSE_PAREN
    """
    p[0] = []

def p_formal_arguments_list(p):
    """
    FormalArguments : OPEN_PAREN ArgumentList CLOSE_PAREN
    """
    p[0] = p[2]

def p_argument_list_single(p):
    """
    ArgumentList : Expr
    """
    p[0] = [p[1]]

def p_argument_list_recursive(p):
    """
    ArgumentList : ArgumentList COMMA Expr
    """
    p[0] = p[1]
    p[0].append(p[3])

#
# error handling
#

def p_error(p):
    #FIXME: Other cases where p is None?
    if p is None:
        p = '[END-OF-INPUT]'
    raise RuntimeError("Syntax error at '{0}'".format(p))


#import ply.yacc as yacc
# Build the parser
#parser = yacc.yacc()
