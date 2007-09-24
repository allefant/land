"""
The syntax analyzer takes a tree of nodes as output by the parser and transforms
it into an abstract syntax tree, ready to be compiled.
"""

import node, token
static import parser, expression

class SyntaxAnalyzer:
    LM_Node *root
    LM_Tokenizer *tokenizer
    # The parser keeps track of all allocated nodes, so we keep it around.
    void *parser

SyntaxAnalyzer *def syntax_analyzer_new_from_tokenizer(LM_Tokenizer *tokenizer):
    SyntaxAnalyzer *self
    land_alloc(self)
    self->tokenizer = tokenizer
    return self

def syntax_analyzer_destroy(SyntaxAnalyzer *self):
    parser_del(self->parser)
    land_free(self)

def syntax_analyzer_parse(SyntaxAnalyzer *self, int debug):
    Parser *p = parser_new_from_tokenizer(self->tokenizer)
    parser_parse(p, debug)
    self->root = p->root
    self->parser = p

static void block(SyntaxAnalyzer *sa, LM_Node *node);

static def statement(SyntaxAnalyzer *sa, LM_Node *node):
    # Check if this is a block statement.
    if node->last->type == LM_NODE_BLOCK:
        if node->first->type == LM_NODE_TOKEN:
            LM_Token *token = node->first->data
            if token->type == TOKEN_ALPHANUM:
                int isif = !strcmp(token->string, "if")
                int iselse = !strcmp(token->string, "else")
                int iselif = !strcmp(token->string, "elif")
                int iswhile = !strcmp(token->string, "while")
                if isif or iselse or iselif or iswhile:

                    node->first->type = LM_NODE_OPERATION

                    LM_Node *bloc = node->last
                    LM_Node *expr = None

                    if node->first->next != bloc:
                        while 1:
                            if not expression(sa, node->first->next): break
                        expr = node->first->next

                    block(sa, bloc)

                    if expr:
                        lm_node_remove(expr)
                        lm_node_add_child(node->first, expr)
                    lm_node_remove(bloc)
                    lm_node_add_child(node->first, bloc)

                    if isif or iswhile:
                        node->type = LM_NODE_STATEMENT_CONDITIONAL

                    if iselse or iselif:
                        LM_Node *prev = node->prev
                        if not prev:
                            fprintf(stderr, "%s without if\n", token->string)
                            return
                        lm_node_remove(node)
                        LM_Node *elsenode = node->first
                        lm_node_remove(elsenode)
                        lm_node_add_child(prev, elsenode)
                    return

        node->type = LM_NODE_FUNCTION
        block(sa, node->last)
        return

    # Check if this is a special case of a function-used-as-statement, where
    # the first token is the statement and should not be mangled by the
    # expression mechanism.
    int is_statement = 0
    if node->first->type == LM_NODE_TOKEN:
        LM_Token *token = node->first->data
        if token->type == TOKEN_ALPHANUM:
            LM_Node *next = node->first->next
            if not next:
                is_statement = 1
            elif next->type == LM_NODE_TOKEN:
                token = next->data
                if token->type != TOKEN_SYMBOL or\
                    not ustrcmp(token->string, "("):
                    is_statement = 1

    if is_statement:
        node->first->type = LM_NODE_OPERATION
        if node->first->next:
            while 1:
                if not expression(sa, node->first->next): break
            LM_Node *argument = node->first->next
            lm_node_remove(argument)
            
            lm_node_add_child(node->first, argument)
    else:
        while 1:
            if not expression(sa, node->first): break

static def block(SyntaxAnalyzer *sa, LM_Node *node):
    node = node->first
    while node:
        LM_Node *next = node->next
        statement(sa, node)
        node = next

def syntax_analyzer_analyze(SyntaxAnalyzer *self, int debug):
    """
    Converts a parse tree into a syntax tree. That is, expressions and operator
    precedences are considered.
    """
    LM_Node *node = self->root->first
    while node:
        LM_Node *next = node->next
        block(self, node)
        node = next

    if debug: lm_node_debug(self->root, 0)
