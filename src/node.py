import global land
static import token

enum LM_NodeType:
    LM_NODE_INVALID

    LM_NODE_BLOCK
    LM_NODE_STATEMENT
    LM_NODE_TOKEN

    LM_NODE_OPERAND
    LM_NODE_OPERATION
    LM_NODE_FUNCTION

    LM_NODE_STATEMENT_CONDITIONAL

class LM_Node:
    LM_NodeType type
    void *data
    LM_Node *first, *last
    LM_Node *next, *prev
    LM_Node *parent

LM_Node *def lm_node_new(LM_NodeType type, void *data):
    LM_Node *self
    land_alloc(self)
    self->type = type
    self->data = data
    return self

def lm_node_del(LM_Node *self):
    land_free(self)

def lm_node_add_child(LM_Node *self, LM_Node *child):
    child->parent = self
    child->next = None
    child->prev = self->last
    if self->last:
        self->last->next = child
    else:
        self->first = child
    self->last = child

def lm_node_remove(LM_Node *self):
    if not self->parent: return
    if self->next:
        self->next->prev = self->prev
    else:
        self->parent->last = self->prev
    if self->prev:
        self->prev->next = self->next
    else:
        self->parent->first = self->next

char const *def lm_node_print(LM_Node *self):
    static char str[256]
    if self->type == LM_NODE_BLOCK:
        uszprintf(str, sizeof str, "BLOCK")
    elif self->type == LM_NODE_STATEMENT:
        uszprintf(str, sizeof str, "STATEMENT")
    elif self->type == LM_NODE_STATEMENT_CONDITIONAL:
        uszprintf(str, sizeof str, "NODE_STATEMENT_CONDITIONAL")
    elif self->type == LM_NODE_FUNCTION:
        uszprintf(str, sizeof str, "FUNCTION")
    elif self->type == LM_NODE_OPERAND:
        Token *token = self->data
        uszprintf(str, sizeof str, "OPERAND «%s» (%d)", token->string,
            token->type)
    elif self->type == LM_NODE_OPERATION:
        Token *token = self->data
        uszprintf(str, sizeof str, "NODE_OPERATION «%s» (%d)", token->string,
            token->type)
    elif self->type == LM_NODE_TOKEN:
        Token *token = self->data
        uszprintf(str, sizeof str, "TOKEN «%s» (%d)", token->string,
            token->type)
    else:
        uszprintf(str, sizeof str, "(node %d)", self->type)
    return str

def lm_node_debug(LM_Node *self, int indent):
    for int i = 0; i < indent; i++:
        printf("    ")
    char const *s = lm_node_print(self)
    printf("%s\n", s)
    if self->first: lm_node_debug(self->first, indent + 1)

    if self->next:
        lm_node_debug(self->next, indent)
    