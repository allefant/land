"""
The parser is a pass following after the tokenizer and before the syntax
analyzer. Basically, it parses the flat list of tokens into a tree of nodes,
utilizing the special indentation rules (as well as the alternate tokens
";", ":" and "end").
"""

import global land
import node, token

class Parser:
    Node *root
    Token *token

static Node *parse_block(Parser *self);

Parser *def parser_new_from_tokenizer(Tokenizer *tokenizer):
    Parser *self
    land_alloc(self)
    self->token = tokenizer->first
    return self

def parser_del(Parser *self):
    """
    The generated nodes are not deleted, they are owned by the caller now.
    """
    land_free(self)

static Node *def parse_statement(Parser *self):
    Node *statement_node = node_new(NODE_STATEMENT, None)
    Token *first_token = self->token
    if not strcmp(self->token->string, ";"):
        self->token = self->token->next
        return None
    if not strcmp(self->token->string, "end"):
        self->token = self->token->next
        return None
    Node *first_node = node_new(NODE_TOKEN, first_token)
    node_add_child(statement_node, first_node)
    self->token = self->token->next
    while self->token:
        if self->token->line > first_token->line: break
        if not strcmp(self->token->string, ";"):
            self->token = self->token->next
            if self->token:
                self->token->column = first_token->column
            break
        if not strcmp(self->token->string, ":"):
            self->token = self->token->next
            break

        Node *token_node = node_new(NODE_TOKEN, self->token)
        node_add_child(statement_node, token_node)

        self->token = self->token->next

    if self->token:
        if self->token->column > first_token->column:
            node_add_child(statement_node, parse_block(self))

    return statement_node

static Node *def parse_block(Parser *self):
    Node *node = node_new(NODE_BLOCK, None)

    if self->token:
        int indent = self->token->column
        while self->token:
            if self->token->column < indent: break
            Node *statement = parse_statement(self)
            if statement:
                node_add_child(node, statement)
            else:
                break
    return node

def parser_parse(Parser *self):
    """
    Converts a flat list of tokens into a tree of functions and statements.
    """
    self->root = parse_block(self)

    Node *n = self->root
    if n: node_debug(n, 0)
