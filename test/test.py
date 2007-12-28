#!/usr/bin/env python
# encoding: utf8
import unittest
import subprocess

class Test(unittest.TestCase):
    def execute(self, basename, code, result):
        name = "test/" + basename

        f = file(name + ".spell", "w")
        f.write(code)
        f.close()

        # Compile
        p = subprocess.Popen(["./landmagic", "compile",
            name + ".spell", name + ".code"],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)
        p.wait()
        self.failUnless((p.returncode == 0), msg = p.stderr.read())

        # Execute
        p = subprocess.Popen(["./landmagic", "execute",
            name + ".code"],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)
        p.wait()

        output = p.stdout.read()
        err = p.stderr.read()

        self.failUnless((p.returncode == 0), msg = err)

        self.failUnless((output == result), msg = err + output)

    def test_function(self):
        self.execute("function", """
helloworld
    print "Aia Ilu"

helloworld""",
            "Aia Ilu\n")
    
    def test_string(self):
        self.execute("string", r"""
    print "'quotes'"
    print '"quotes"'
    print '\'quotes\''
    print "\"quotes\""
    print ''''quotes\''''""" + """
    print \"\"\"\"quotes\\\"\"\"\"""" + r"""
    print "\\backslash"
    print "new
line"
    print "new\nline"
""",
            """'quotes'\n"quotes"\n'quotes'\n"quotes"\n'quotes'\n"quotes"\n\\backslash\nnew\nline\nnew\nline\n""")

    def test_argument(self):
        self.execute("argument", """
helloworld x
    print x

helloworld "Aia Ilu"
""",
            "Aia Ilu\n")

    def test_arguments(self):
        self.execute("arguments", """
helloworld x, y
    print x, y

helloworld "Aia", "Ilu"
""",
            "Aia Ilu\n")

    def test_expressions(self):
        self.execute("expressions", """
print 1 + 2
print 1 + 2 + 3
print 1 + 2 * 3 + 4
print (1 + 2) * 3 + 4
print (1)
print ((2))
print 1 - 2 - 3 - 4
print 1 - (2 - (3 - (4)))
print (1 + 2) * (3 + 4), (5 + 6) / (7 - 8)
print(5 * (3 - 1))
""", "3\n6\n11\n13\n1\n2\n-8\n-2\n21 -11\n10\n")


    def test_closure(self):
        self.execute("closure", """
kau = 0

foo x
    bar y
        print x + y
    kau = bar

foo 3
kau 4
""", "7\n")

    def test_if(self):
        self.execute("if", """
if 1 > 0
    print "a"
print "b"
""", "a\nb\n")

    def test_else(self):
        self.execute("else", """
if 1 > 1
    print "a"
else
    print "b"
""", "b\n")

    def test_elif(self):
        self.execute("elif", """
if 1 > 1
    print "a"
elif 2 > 1
    print "b"
else
    print "c"
print "d"
""", "b\nd\n")

    def test_or(self):
        self.execute("or", """
a = 0
b = 0
c = 0
if a or b or c
    print "yes"
else
    print "no"
a = 1
b = 0
c = 0
if a or b or c
    print "yes"
else
    print "no"
a = 0
b = 1
c = 0
if a or b or c
    print "yes"
else
    print "no"
a = 1
b = 1
c = 1
if a or b or c
    print "yes"
else
    print "no"
""", "no\nyes\nyes\nyes\n")

    def test_and(self):
        self.execute("and", """
a = 0
b = 0
c = 0
if a and b and c
    print "yes"
else
    print "no"
a = 1
b = 0
c = 0
if a and b and c
    print "yes"
else
    print "no"
a = 0
b = 1
c = 0
if a and b and c
    print "yes"
else
    print "no"
a = 1
b = 1
c = 1
if a and b and c
    print "yes"
else
    print "no"
""", "no\nno\nno\nyes\n")

    def test_break(self):
        self.execute("break", """
x = 0
while x < 10
    print x
    if x == 7
        break
    elif x == 3
        x = x * 2
        continue
    x = x + 1
""", "0\n1\n2\n3\n6\n7\n")

    def test_oneline(self):
        self.execute("oneline", """
x = 0; while x < 10: print x; if x == 7: break; ; elif x == 3: x = x * 2; continue; ; x = x + 1
""", "0\n1\n2\n3\n6\n7\n")

    def test_oneline2(self):
        self.execute("oneline2", """
x = 0; while x < 10: print x; if x == 7: break; end elif x == 3: x = x * 2; continue; end x = x + 1
""", "0\n1\n2\n3\n6\n7\n")

    def test_dict(self):
        self.execute("dict", """
x = {}
x."a " = "A"
x.b = {}
print x
x.b.c = "C"
print x
print x."a "
""", "{a  = A, b = {}}\n{a  = A, b = {c = C}}\nA\n")

    def test_dict2(self):
        self.execute("dict2", """
x = {}
x["a "] = "A"
x["b"] = {}
print x
x["b"]["c"] = "C"
print x
print x["a "]
""", "{a  = A, b = {}}\n{a  = A, b = {c = C}}\nA\n")

    def test_return(self):
        self.execute("return", """
add a, b
    return a + b
print add(1, 2)
""", "3\n")

    def test_external(self):
        self.execute("external", """
use test
test
test 1
test(1, 2, "Hola.", "¿Cómo estás?")
""", "test\ntest 1\ntest 1 2 Hola. ¿Cómo estás?\n")

    def test_truth(self):
        self.execute("truth", """
if 1
    print "yes"
if 0
    print "no"
""", "yes\n")

    def test_funcvar(self):
        self.execute("funcvar", """
foo:
    print "foo"
bar
    print "bar"
goo: print "goo"
i = 0
while i < 3
    if i == 0: x = foo
    if i == 1: x = bar
    if i == 2: x = goo
    x()
    i = i + 1
""", "foo\nbar\ngoo\n")

    def test_pass(self):
        self.execute("pass", """
foo:
    pass
foo
""", "")

    def test_none(self):
        self.execute("none", """
empty: pass
x = none
y = empty
z = y()
if x == z: print "none"
""", "none\n")

    def test_forward(self):
        self.execute("forward", """
main:
    forward

forward:
    print "forward"

main
""", "forward\n")

    def test_userdict(self):
        self.execute("userdict", """
use userdict

userdict.x = "a"
y = userdict.y
""", "set x a\nget y\n")

    def test_floatliteral(self):
        self.execute("floatliteral", """
print 0.2 / 5
""", "0.040000\n")

    def test_in(self):
        self.execute("in", """
x = {}
x.a = 1
print "a" in x
print "b" in x
""", "1\n0\n")

    def test_bracket(self):
        self.execute("bracket", """
x = {}
x.a = "b"
y = {}
y.b = {}
y[x.a].c = "d"
y.b.d = "ok"
print y[x["a"]][y[x["a"]]["c"]]
""", "ok\n")

    def test_keywords(self):
        self.execute("keywords", """
test a, ...:
    keywords = ...
    print a, keywords.a
test(1, a = 2)
""", "1 2\n")

    def test_dictionary(self):
        self.execute("dictionary", """
x = {a = 1,
    b = 2,
    c = 3 * 3, d = 4}
print x
""", "{a = 1, b = 2, c = 9, d = 4}\n")

    def test_implicit_return(self):
        self.execute("implicit-return", """
foo: return 7
bar: foo
print bar()
""", "7\n")

    def test_line_continuation(self):
        self.execute("line-continuation", """
y = 0
foo a b c: y = a + b + c
x = (1 + 2
    + 3)
foo 1, 2,
    3
print x, y
""", "6 6\n")

    def test_varargs(self):
        self.execute("varargs", """
foo a, ...
    b = ...
    print a, b
foo
foo 0
foo x = 2
foo 0, x = 2
""", "none none\n0 none\nnone {x = 2}\n0 {x = 2}\n")

    def test_dictadd(self):
        self.execute("dictadd", """
x = {a = 1, b = 2}
y = {b = 20, c = 30}
z = x + y
print z
""", "{a = 1, b = 20, c = 30}\n")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity = 2).run(suite)
