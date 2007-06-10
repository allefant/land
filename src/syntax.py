"""
The syntax analyzer takes a tree of nodes as output by the parser and transforms
it into an abstract syntax tree, ready to be compiled.
"""

import node, token
static import parser, expression

class SyntaxAnalyzer:
    Node *root
    Tokenizer *tokenizer

SyntaxAnalyzer *def syntax_analyzer_new_from_tokenizer(Tokenizer *tokenizer):
    SyntaxAnalyzer *self
    land_alloc(self)
    self->tokenizer = tokenizer
    return self

def syntax_analyzer_parse(SyntaxAnalyzer *self):
    Parser *p = parser_new_from_tokenizer(self->tokenizer)
    parser_parse(p)
    self->root = p->root
    parser_del(p)

static void block(SyntaxAnalyzer *sa, Node *node);

static def statement(SyntaxAnalyzer *sa, Node *node):
    # Check if this is a block statement.
    if node->last->type == NODE_BLOCK:
        if node->first->type == NODE_TOKEN:
            Token *token = node->first->data
            if token->type == TOKEN_ALPHANUM:
                int isif = !strcmp(token->string, "if")
                int iselse = !strcmp(token->string, "else")
                int iselif = !strcmp(token->string, "elif")
                int iswhile = !strcmp(token->string, "while")
                if isif or iselse or iselif or iswhile:

                    node->first->type = NODE_OPERATION

                    Node *bloc = node->last
                    Node *expr = None

                    if node->first->next != bloc:
                        while 1:
                            if not expression(sa, node->first->next): break
                        expr = node->first->next

                    block(sa, bloc)

                    if expr:
                        node_remove(expr)
                        node_add_child(node->first, expr)
                    node_remove(bloc)
                    node_add_child(node->first, bloc)

                    if isif or iswhile:
                        node->type = NODE_STATEMENT_CONDITIONAL

                    if iselse or iselif:
                        Node *prev = node->prev
                        if not prev:
                            fprintf(stderr, "%s without if\n", token->string)
                            return
                        node_remove(node)
                        Node *elsenode = node->first
                        node_remove(elsenode)
                        node_add_child(prev, elsenode)
                    return

        node->type = NODE_FUNCTION
        block(sa, node->last)
        return

    # Check if this is a special case of a function-used-as-statement, where
    # the first token is the statement and should not be mangled by the
    # expression mechanism.
    int is_statement = 0
    if node->first->type == NODE_TOKEN:
        Token *token = node->first->data
        if token->type == TOKEN_ALPHANUM:
            Node *next = node->first->next
            if not next:
                is_statement = 1
            elif next->type == NODE_TOKEN:
                token = next->data
                if token->type != TOKEN_SYMBOL or\
                    not ustrcmp(token->string, "("):
                    is_statement = 1

    if is_statement:
        node->first->type = NODE_OPERATION
        if node->first->next:
            while 1:
                if not expression(sa, node->first->next): break
            Node *argument = node->first->next
            node_remove(argument)
            
            node_add_child(node->first, argument)
    else:
        while 1:
            if not expression(sa, node->first): break

static def block(SyntaxAnalyzer *sa, Node *node):
    node = node->first
    while node:
        Node *next = node->next
        statement(sa, node)
        node = next

def syntax_analyzer_analyze(SyntaxAnalyzer *self):
    """
    Converts a parse tree into a syntax tree. That is, expressions and operator
    precedences are considered.
    """
    block(self, self->root)

    node_debug(self->root, 0)
