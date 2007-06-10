import global land
static import token

enum NodeType:
    NODE_INVALID

    NODE_BLOCK
    NODE_STATEMENT
    NODE_TOKEN

    NODE_OPERAND
    NODE_OPERATION
    NODE_FUNCTION

    NODE_STATEMENT_CONDITIONAL

class Node:
    NodeType type
    void *data
    Node *first, *last
    Node *next, *prev
    Node *parent

Node *def node_new(NodeType type, void *data):
    Node *self
    land_alloc(self)
    self->type = type
    self->data = data
    return self

def node_add_child(Node *self, Node *child):
    child->parent = self
    child->next = None
    child->prev = self->last
    if self->last:
        self->last->next = child
    else:
        self->first = child
    self->last = child

def node_remove(Node *self):
    if not self->parent: return
    if self->next:
        self->next->prev = self->prev
    else:
        self->parent->last = self->prev
    if self->prev:
        self->prev->next = self->next
    else:
        self->parent->first = self->next

char const *def node_print(Node *self):
    static char str[256]
    if self->type == NODE_BLOCK:
        uszprintf(str, sizeof str, "BLOCK")
    elif self->type == NODE_STATEMENT:
        uszprintf(str, sizeof str, "STATEMENT")
    elif self->type == NODE_STATEMENT_CONDITIONAL:
        uszprintf(str, sizeof str, "NODE_STATEMENT_CONDITIONAL")
    elif self->type == NODE_FUNCTION:
        uszprintf(str, sizeof str, "FUNCTION")
    elif self->type == NODE_OPERAND:
        Token *token = self->data
        uszprintf(str, sizeof str, "OPERAND «%s» (%d)", token->string,
            token->type)
    elif self->type == NODE_OPERATION:
        Token *token = self->data
        uszprintf(str, sizeof str, "NODE_OPERATION «%s» (%d)", token->string,
            token->type)
    elif self->type == NODE_TOKEN:
        Token *token = self->data
        uszprintf(str, sizeof str, "TOKEN «%s» (%d)", token->string,
            token->type)
    else:
        uszprintf(str, sizeof str, "(node %d)", self->type)
    return str

def node_debug(Node *self, int indent):
    for int i = 0; i < indent; i++:
        printf("    ")
    char const *s = node_print(self)
    printf("%s\n", s)
    if self->first: node_debug(self->first, indent + 1)

    if self->next:
        node_debug(self->next, indent)
    