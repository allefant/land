"""
The parser is a pass following after the tokenizer and before the syntax
analyzer. Basically, it parses the flat list of tokens into a tree of nodes,
utilizing the special indentation rules (as well as the alternate tokens
";", ":" and "end").
"""

import global land
import node, token

class Parser:
    LM_Node *root
    LandArray *allocated_nodes
    Token *token

static LM_Node *parse_block(Parser *self);

static LM_Node *def node_new(Parser *self, LM_NodeType type, void *data):
    LM_Node *n = lm_node_new(type, data)
    land_array_add(self->allocated_nodes, n)
    return n

Parser *def parser_new_from_tokenizer(Tokenizer const *tokenizer):
    """
    You must keep the tokenizer around until the parser is destroyed first.
    """
    Parser *self
    land_alloc(self)
    self->token = tokenizer->first
    self->allocated_nodes = land_array_new()
    return self

def parser_del(Parser *self):
    """
    The generated nodes are not deleted, they are owned by the caller now. And
    the tokens are still owned by the tokenizer.
    """
    for int i = 0; i < self->allocated_nodes->count; i++:
        LM_Node *n = land_array_get_nth(self->allocated_nodes, i)
        lm_node_del(n)
    land_array_destroy(self->allocated_nodes)
    land_free(self)

static LM_Node *def parse_statement(Parser *self):
    LM_Node *statement_node = node_new(self, LM_NODE_STATEMENT, None)
    Token *first_token = self->token
    if not strcmp(self->token->string, ";"):
        self->token = self->token->next
        return None
    if not strcmp(self->token->string, "end"):
        self->token = self->token->next
        return None
    LM_Node *first_node = node_new(self, LM_NODE_TOKEN, first_token)
    lm_node_add_child(statement_node, first_node)
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

        LM_Node *token_node = node_new(self, LM_NODE_TOKEN, self->token)
        lm_node_add_child(statement_node, token_node)

        self->token = self->token->next

    if self->token:
        if self->token->column > first_token->column:
            lm_node_add_child(statement_node, parse_block(self))

    return statement_node

static LM_Node *def parse_block(Parser *self):
    LM_Node *node = node_new(self, LM_NODE_BLOCK, None)

    if self->token:
        int indent = self->token->column
        while self->token:
            if self->token->column < indent: break
            LM_Node *statement = parse_statement(self)
            if statement:
                lm_node_add_child(node, statement)
            else:
                break
    return node

def parser_parse(Parser *self, int debug):
    """
    Converts a flat list of tokens into a tree of functions and statements.
    """
    self->root = parse_block(self)

    LM_Node *n = self->root
    if n and debug: lm_node_debug(n, 0)
