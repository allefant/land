"""
The expression parser. This is a crucial part of the syntax analyzer.
"""
import compiler, node, token

static int def is_operator(Node *node):
    if node->type == NODE_TOKEN:
        Token *token = node->data
        if token->type == TOKEN_SYMBOL:
            return 1
        if not strcmp(token->string, "or"):
            return 1
        if not strcmp(token->string, "and"):
            return 1
    return 0

static int def is_operand(Node *node):
    if node->type == NODE_OPERATION:
        return 1
    if node->type == NODE_OPERAND:
        return 1
    if node->type == NODE_TOKEN:
        Token *token = node->data
        if token->type == TOKEN_ALPHANUM:
            return 1
        if token->type == TOKEN_STRING:
            return 1
    return 0

static int def is_symbol(Node *node, char const *symbol):
    if node->type == NODE_TOKEN:
        Token *token = node->data
        if token->type == TOKEN_SYMBOL:
            if not ustrcmp(token->string, symbol):
                return 1
    return 0

static int def is_opening_parenthesis(Node *node):
    return is_symbol(node, "(")

static int def is_closing_parenthesis(Node *node):
    return is_symbol(node, ")")

static int def operator_precedence(Node *left, Node *right):
    """
    Returns 1 if left has precedence over right.
    """
    Token *tok1 = left->data
    Token *tok2 = right->data

    # a, b, c -> a, (b, c)
    # a, b + c -> a, (b + c)
    # a, b = c -> a, (b = c)
    if not strcmp(tok1->string, ","): # a , b ?
        return 0

    if not strcmp(tok2->string, "("): # a ? b (
        return 0

    if not ustrcmp(tok1->string, "."): # a . b ?
        if not ustrcmp(tok2->string, "."): # a . b . c = a . (b . c)
            return 0

    if not strcmp(tok1->string, "="): # a = b ?
        if strcmp(tok2->string, ","):
            return 0

    if not strcmp(tok1->string, "+"): # a + b ?
        if not ustrcmp(tok2->string, "*"): # a + b * c
            return 0
        if not ustrcmp(tok2->string, "/"): # a + b / c
            return 0
        if not ustrcmp(tok2->string, "."): # a + b . c
            return 0

    if not strcmp(tok1->string, "-"): # a - b ?
        if not ustrcmp(tok2->string, "*"): # a - b * c
            return 0
        if not ustrcmp(tok2->string, "/"): # a - b / c
            return 0
        if not ustrcmp(tok2->string, "."): # a - b . c
            return 0

    # a or b < 2 -> a or (b < 2)
    # a or b or c -> a or (b or c)
    # a or b and c -> a or (b and c)
    if not strcmp(tok1->string, "or"):
        return 0
    # a and b or c -> a and (b or c)
    if not strcmp(tok1->string, "and"):
        return 0

    return 1 

int def expression(SyntaxAnalyzer *self, Node *node):
    if is_symbol(node, "{"):
        Node *opening = node
        node = node->next
        if is_symbol(node, "}"):
            node_remove(node)
        else:
            token_err(self->tokenizer, node->data,
                "Sorry, dictionary syntax not supported yet in this version.")
            return 0
        opening->type = NODE_OPERAND
        return 1

    if is_opening_parenthesis(node):
        while 1:
            if not expression(self, node->next): break
        if is_closing_parenthesis(node->next):
            node_remove(node->next)
            node->type = NODE_OPERATION
            return 1
        Node *inside = node->next;
        Node *closing = node->next->next;
        if not closing or not is_closing_parenthesis(closing):
            token_err(self->tokenizer, node->data,
                "No matching closing parenthesis found.")
            return 0
        node_remove(closing)
        node_remove(inside)
        if inside->type == NODE_TOKEN:
            inside->type = NODE_OPERAND
        node->type = NODE_OPERATION
        node_add_child(node, inside)
        # FIXME: Do we need to free closing here, or is it still referenced
        # somewhere else?
        return 1
    
    elif is_operand(node): # x
        Node *left = node
        node = node->next
        if not node:
            # Just an identifier on its own - treat it as variable
            # So e.g. "x = foobar" will not call foobar, only "x = foobar()"
            # will.
            if left->type == NODE_TOKEN:
                left->type = NODE_OPERAND
            return 0
        elif node->type == NODE_STATEMENT: return 0
        elif is_closing_parenthesis(node): return 0
        elif is_opening_parenthesis(node): # x (
            expression(self, node)
            node_remove(node)
            left->type = NODE_OPERATION
            node_add_child(left, node)
            return 1
        elif is_operator(node): # x +
            Node *operator = node
            node = node->next
            if is_opening_parenthesis(node): # x + (
                return expression(self, node)
            elif is_symbol(node, "{"): # x + {
                return expression(self, node)
            elif is_operand(node): # x + y
                Node *right = node
                node = node->next
                int reduce = 0
                if not node: reduce = 1
                elif node->type == NODE_STATEMENT: reduce = 1
                elif node->type == NODE_BLOCK: reduce = 1
                elif is_closing_parenthesis(node): reduce = 1
                elif is_operator(node): # x + y +
                    if operator_precedence(operator, node):
                        reduce = 1
                if reduce:
                    node_remove(left)
                    if left->type == NODE_TOKEN:
                        left->type = NODE_OPERAND
                    node_remove(right)
                    if right->type == NODE_TOKEN:
                        right->type = NODE_OPERAND
                    operator->type = NODE_OPERATION
                    node_add_child(operator, left)
                    node_add_child(operator, right)
                    return 1
                else:
                    return expression(self, right)
        elif is_operand(node): # x y
            # We always reduce.
            node_remove(node)
            left->type = NODE_OPERATION
            node_add_child(left, node)
            return 1
    return 0