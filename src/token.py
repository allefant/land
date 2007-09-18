"""
The tokenizer reads in text and outputs a list of tokens. This removes
whitespace and comments and groups names, number and strings into single
tokens.
"""

import global land, ctype

enum TokenType:
    TOKEN_INVALID
    TOKEN_ALPHANUM
    TOKEN_SYMBOL
    TOKEN_STRING

class Token:
    """
    Represents one token in a file.
    """
    char *string
    int line
    int column
    TokenType type
    Token *next

class Tokenizer:
    char *filename
    LandBuffer *text
    int line
    int linestart
    int pos
    int end
    Token *first
    Token *token

def token_err(Tokenizer const *self, Token *t, char const *str, ...):
    fprintf(stderr, "%s: %d: %d: ", self->filename, 1 + t->line, 1 + t->column)
    va_list arg
    va_start(arg, str)
    vfprintf(stderr, str, arg)
    va_end(arg)
    fprintf(stderr, "\n")

static def token_add(Tokenizer *self, TokenType type, int linenum, column,
    char *string):
    Token *token
    land_alloc(token)
    token->line = linenum
    token->column = column
    token->type = type
    token->string = string
    token->next = None
    if self->token:
        self->token->next = token
    else:
        self->first = token
    self->token = token

Tokenizer *def tokenizer_new_from_file(char const *filename):
    LandBuffer *buffer = land_buffer_read_from_file(filename)
    if not buffer: return None
    Tokenizer *self
    land_alloc(self)
    self->filename = land_strdup(filename)
    self->text = buffer
    return self

def tokenizer_destroy(Tokenizer *self):
    for Token *t = self->first; t;:
        Token *next = t->next
        land_free(t->string)
        land_free(t)
        t = next
    land_buffer_del(self->text)
    land_free(self->filename)
    land_free(self)

static char def next(Tokenizer *self):
    char c = self->text->buffer[self->pos++]
    if self->pos == self->text->n:
        self->end = 1
    if c == 10:
        self->line++
        self->linestart = self->pos
    return c

static char def peek(Tokenizer *self, int i):
    if self->pos + i < self->text->n:
        return self->text->buffer[self->pos + i]
    else:
        return 0

static char const *multichar_symbol_tokens[] = {
    "==",
    ">=",
    "<=",
    "<>",
    "<<=",
    ">>=",
    "->",
    "<<",
    ">>",
    "!=",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "~=",
    "|=",
    "&=",
    "^=",
    None
    }

static def add_operator(Tokenizer *self):
    char string[16]
    for int i = 0; ; i++:
        char const *mc = multichar_symbol_tokens[i]
        if not mc:
            string[0] = self->text->buffer[self->pos - 1]
            string[1] = '\0'
            break
        if not strncmp(mc, self->text->buffer + self->pos - 1, strlen(mc)):
            strcpy(string, mc)
            self->pos += strlen(mc) - 1
            break

    token_add(self, TOKEN_SYMBOL,
        self->line, self->pos - self->linestart - 1, land_strdup(string))

static def skip_comment(Tokenizer *self):
    while not self->end:
        if next(self) == 10: break

static def get_token(Tokenizer *self):
    int start = self->pos - 1
    char first = self->text->buffer[start]
    while self->pos < self->text->n:
        char c = self->text->buffer[self->pos]
        if not isalnum(c) and  c != '_':
            if not isdigit(first) or c != '.':
                break
        next(self) # would return the same c we already handled above

    int n = self->pos - start
    char *string = land_malloc(1 + n)
    memcpy(string, self->text->buffer + start, n)
    string[n] = 0

    token_add(self, TOKEN_ALPHANUM, self->line, start - self->linestart, string)

static def get_string_triple(Tokenizer *self, char delimiter, int triple):
    int linenum = self->line
    int column = self->pos - self->linestart

    int dpos = 0
    int escape = 0
    LandBuffer *buffer = land_buffer_new()
    while not self->end:
        char c = next(self)

        if dpos:
            if c == delimiter:
                dpos++
                if dpos == 3: break
                continue
            else:
                if dpos == 1: land_buffer_add_char(buffer, delimiter)
                if dpos == 2: land_buffer_add_char(buffer, delimiter)
                dpos = 0

        if escape:
            escape = 0
            if c == 'a':
                c = 7
            elif c == 'b':
                c = 8
            elif c == 't':
                c = 9
            elif c == 'n':
                c = 10
            elif c == 'v':
                c = 11
            elif c == 'f':
                c = 12
            elif c == 'r':
                c = 13
            elif c == '0':
                c = 0
        else:
            if c == '\\':
                escape = 1
                continue
            elif c == delimiter:
                if triple:
                    dpos++
                    continue
                else: break

        land_buffer_add_char(buffer, c)

    token_add(self, TOKEN_STRING, linenum, column, land_buffer_finish(buffer))

static def get_string(Tokenizer *self, char delimiter):
    if peek(self, 0) == delimiter and peek(self, 1) == delimiter:
        next(self)
        next(self)
        get_string_triple(self, delimiter, 1)
    else:
        get_string_triple(self, delimiter, 0)

static def find_token(Tokenizer *self):
    while not self->end:
        char c = next(self)
        if isalnum(c) or c == '_':
            get_token(self)
        elif c == '"':
            get_string(self, c)
        elif c == '\'':
            get_string(self, c)
        elif c == '#':
            skip_comment(self)
        elif c > ' ' and c < '':
            add_operator(self)
        else:
            pass # Ignore anything else.

def tokenizer_tokenize(Tokenizer *self, int debug):
    """
    Comments: Anything after #
    Tokens: alphanumeric and _
    Strings: single and double quotes, backslash escapes, may contain newlines
    Triple Strings: same, but no need to escape quotes themselves
    """
    find_token(self)
    Token *t = self->first
    while t:
        if debug: printf("%3d:%3d: «%s»\n", t->line + 1, t->column + 1, t->string)
        t = t->next
