"""dumper

Dump Python data structures (including class instances) in a nicely-
nested, easy-to-read form.  Handles recursive data structures properly,
and has sensible options for limiting the extent of the dump both by
simple depth and by some rules for how to handle contained instances.

Copyright (c) 2009 Python Software Foundation
Copyright (c) 2014,2018 Joshua Richardson, Chegg Inc.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. The name of the author may not be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

This code orinally hosted at:
  https://svn.python.org/packages/branches/egginfo/dumper.py
"""



"""Dumping is generally accessed through the 'dump()' function:

    dump (any_python_object)

and is controlled by setting module-level global variables:

    import dumper

    dumper.max_depth = 10           # default is 5
    dumper.dump (really_deep_object)

'dump()' is nearly equivalent to 'print' with backquotes for
non-aggregate values (ie. anything *except* lists, tuples, dictionaries,
and class instances).  That is, strings, integers, floats, and other
numeric types are printed out "as-is", and funkier things like class
objects, function objects, and type objects are also dumped using their
traditional Python string representation.  For example:

    >>> dump ("Hello" + "world")
    'Helloworld'
    >>> class Foo: pass
    >>> dump (Foo)
    <class __main__.Foo at 271050>

'dump()' is slightly more interesting than 'print' for "short" lists,
tuples, and dictionaries.  (Lists and tuples are "short" when they have
no more than 10 elements and all elements are strings or numbers;
dictionaries are short when they have no more than 5 key/value pairs and
all keys and values are strings or numbers.)

For "short" lists and tuples, you get the 'id()' of the object and its
contents on one line:

    >>> dump (['foo', 3])
    <list at 0x242cb8> ['foo', 3]
    >>> dump ((3+4j, 'blah', 2L**50))
    <tuple at 0x20f208> ((3+4j), 'blah', 1125899906842624L)

"Short" dictionaries are similar:

    >>> d = {'foo': 5, 'bar': 3, 'bonk': 4-3j}
    >>> dump (d)
    <dictionary at 0x2737f0> {'foo': 5, 'bonk': (4-3j), 'bar': 3}

'dump()' is considerably more interesting than 'print' for lists,
tuples, and dictionaries that include more complex objects or are longer
than the 10-element/5-pair limit.  A long but simple list:

    >>> f = open ('/usr/dict/words')
    >>> dump (f.readlines())
    <list at 0x243738>
      0: '10th\012'
      1: '1st\012'
      2: '2nd\012'
    ...
      25138: 'zounds\012'
      25139: "z's\012"
      25140: 'zucchini\012'
      25141: 'Zurich\012'
      25142: 'zygote\012'

(Ellipsis added: 'dump()' just dumps the whole thing.)  Nested lists
also get multiline formatting, no matter how short and simple:

    >>> dump (['nested', ['list']])
    <list at 0x2436c0>
      0: 'nested'
      1: <list at 0x243658> ['list']

Note that since the inner list is "short" it is formatted on one line.
Deeply nested lists and tuples are more fun:

    >>> l = ["top", ('tuple', 'depth', 1), 
    ...      "top again", ["level 1", ["level", 2, ('deep', 'tuple')]]]
    >>> dump (l)
    <list at 0x243798>
      0: 'top'
      1: <tuple at 0x228ca8> ('tuple', 'depth', 1)
      2: 'top again'
      3: <list at 0x243888>
        0: 'level 1'
        1: <list at 0x243580>
          0: 'level'
          1: 2
          2: <tuple at 0x229228> ('deep', 'tuple')

Obviously, this is very handy for debugging complicated data structures.
Recursive data structures are not a problem:

    >>> l = [1, 2, 3]
    >>> l.append (l)
    >>> dump (l)
    <list at 0x243a98>
      0: 1
      1: 2
      2: 3
      3: <list at 0x243a98>: already seen

which is bulkier, but somewhat more informative than "[1, 2, 3, [...]]".

Dictionaries with aggregate keys or values also get multiline displays:

    >>> dump ({(1,0): 'keys', (0,1): 'fun'})
    <dictionary at 0x2754b8>
      (0, 1): 'fun'
      (1, 0): 'keys'

Note that when dictionaries are dumped in multiline format, they are
sorted by key.  In single-line format, 'dump()' just uses 'repr()', so
"short" dictionaries come out in hash order.  Also, no matter how
complicated dictionary *keys* are, they come out all on one line before
the colon.  (Using deeply nested dictionary keys requires a special kind
of madness, though, so you probably know what you're doing if you're
into that.)  Dictionary *values* are treated much like list/tuple
elements (one line if short, indented multiline display if not).

'dump()' is *much* more interesting than 'print' for class instances.
Simple example:

    >>> class Foo:
    ...   def __init__ (self):
    ...     self.a = 37; self.b = None; self.c = self
    ... 
    >>> f = Foo ()
    >>> dump (f)
    <Foo instance at 0x243990> 
      a: 37
      b: None
      c: <Foo instance at 0x243990>: already seen

A more interesting example using a contained instance and more recursion:

    >>> g = Foo ()
    >>> g.a = 42; g.b = [3, 5, 6, f]
    >>> dump (g)
    <Foo instance at 0x243b58> 
      a: 42
      b: <list at 0x243750>
        0: 3
        1: 5
        2: 6
        3: <Foo instance at 0x243990> 
          a: 37
          b: None
          c: <Foo instance at 0x243990>: already seen
      c: <Foo instance at 0x243b58>: already seen

Dumping a large instance that contains several other large instance gets
out of control pretty quickly.  'dump()' has a couple of options to help
you get a handle on this; normally, these are set by assigning to module
globals, but there's a nicer OO way of doing it if you like.  For
example, if you don't want 'dump()' to descend more than 3 levels into
your nested data structure:

    >>> import dumper
    >>> dumper.max_depth = 3
    >>> dumper.dump ([0, [1, [2, [3, [4]]]]])
    <list at 0x240ed0>
      0: 0
      1: <list at 0x240f18>
        0: 1
        1: <list at 0x254800>
          0: 2
          1: <list at 0x254818>: suppressed (too deep)

But note that max_depth does not apply to "short" lists (or tuples or
dictionaries):

    >>> dumper.dump ([0, [1, [2, [3, '3b', '3c']]]])
    <list at 0x240d68>
      0: 0
      1: <list at 0x254878>
        0: 1
        1: <list at 0x254890>
          0: 2
          1: <list at 0x2548c0> [3, '3b', '3c']

Since "short" lists (etc.) can't contain other aggregate objects, this
only bends the "max_depth" limit by one level, though, and it doesn't
increase the amount of output (but it does increase the amount of useful
information in the dump).

'max_depth' is a pretty blunt tool, though; as soon as you set it to N,
you'll find a structure of depth N+1 that you want to see all of.  And
anyways, dumps usually get out of control as a result of dumping large
contained class instances: hence, the more useful control is to tell
'dump()' when to dump contained instances.

The default is to dump contained instances when the two classes (that of
the parent and that of the child) are from the same module.  This
applies to classes defined in the main module or an interactive session
as well, hence:

    >>> class Foo: pass
    >>> class Bar: pass
    >>> f = Foo() ; b = Bar ()
    >>> f.b = b
    >>> f.a = 37
    >>> b.a = 42
    >>> dumper.dump (f)
    <Foo instance at 0x254890> 
      a: 37
      b: <Bar instance at 0x2549b0> 
        a: 42

Note that we have dumped f.b, the contained instance of Bar.  We can
control dumping of contained instances using the 'instance_dump' global;
for example, to completely disable dumping contained instances, set it
to 'none':

    >>> dumper.instance_dump = 'none'
    >>> dumper.dump (f)
    <Foo instance at 0x254890> 
      a: 37
      b: <Bar instance at 0x2549b0> : suppressed (contained instance)

This is the most restrictive mode for contained instance dumping.  The
default mode is 'module', meaning that 'dump()' will only dump contained
instances if both classes (parent and child) were defined in the same
module.  If the two classes were defined in different modules, e.g.

    >>> from foo import Foo
    >>> from bar import Bar
    >>> f = Foo () ; f.a = 42       
    >>> b = Bar () ; b.s = "hello"
    >>> f.child = b

then dumping the container ('f') results in something like

    >>> dumper.dump (f)
    <Foo instance at 0x241308> 
      a: 42
      child: <Bar instance at 0x241578> : suppressed (contained instance from different module)

Of course, you can always explicitly dump the contained instance:

    >>> dumper.dump (f.child)
    <Bar instance at 0x241578> 
      s: 'hello'

The next most permissive level is to dump contained instances as long as
their respective classes were defined in the same package.  Continuing
the above example:

    >>> dumper.instance_dump = 'package'
    >>> dumper.dump (f)
    <Foo instance at 0x241308> 
      a: 42
      child: <Bar instance at 0x241578> 
        s: 'hello'

But if the Foo and Bar classes had come from modules in different
packages, then dumping 'f' would look like:
    
    >>> dumper.dump (f)
    <Foo instance at 0x241350> 
      a: 42
      child: <Bar instance at 0x2415d8> : suppressed (contained instance from different package)

Only if you set 'instance_dump' to its most permissive setting, 'all',
will 'dump()' dump contained instances of classes in completely
different packages:

    >>> dumper.instance_dump = 'all'
    >>> dumper.dump (f)
    <Foo instance at 0x241350> 
      a: 42
      child: <Bar instance at 0x2415d8> 
        s: 'hello'
"""


import sys, string
from types import *

if sys.version < '3':
    integer_types = (int, long,)
    string_types = (basestring,)
    split = string.split
else:
    integer_types = (int,)
    string_types = (str,)
    split = str.split

DICT_TYPES = {type(dict()): 1}
try:
    from BTree import BTree
    DICT_TYPES[BTree] = 1
except ImportError:
    pass
try:
    from BTrees import OOBTree, OIBTree, IOBTree
    DICT_TYPES[OOBTree.OOBTree] = 1
    DICT_TYPES[OIBTree.OIBTree] = 1
    DICT_TYPES[IOBTree.IOBTree] = 1
except ImportError:
    pass

# 
# IDEAS on how to restrict how deep we go when dumping:
#   - never follow cyclic links! (handled with 'seen' hash)
#   - have a maximum dumping depth (for any nestable structure:
#     list/tuple, dictionary, instance)
#   - if in an instance: don't dump any other instances
#   - if in an instance: don't dump instances that belong to classes from
#     other packages
#   - if in an instance: don't dump instances that belong to classes from
#     other modules
# ...ok, these are all implemented now -- cool!

# restrictions on dumping
max_depth = 5
instance_dump = 'module'                # or 'all', 'none', 'package':
                                        # controls whether we dump an
                                        # instance that is under another
                                        # instance (however deep)

# arg -- this is necessary because the .__name__ of a type object
# under JPython is a bit ugly (eg. 'org.python.core.PyList' not 'list')
TYPE_NAMES = {
    BuiltinFunctionType: 'builtin',
    BuiltinMethodType: 'builtin',
    CodeType: 'code',
    type(complex): 'complex',
    type(dict): 'dictionary',
    type(float): 'float',
    FrameType: 'frame',
    FunctionType: 'function',
    type(int): 'int',
    LambdaType: 'function',
    type(list): 'list',
    MethodType: 'instance method',
    ModuleType: 'module',
    type(None): 'None',
    type(string): 'string',
    TracebackType: 'traceback',
    type(tuple): 'tuple',
    type(type): 'type',
    }
try:
    TYPE_NAMES[ClassType] = 'class'
    TYPE_NAMES[DictType] = 'dictionary'
    TYPE_NAMES[DictProxyType] = 'dictionary'
    TYPE_NAMES[EllipsisType] = 'ellipsis'
    TYPE_NAMES[FileType] = 'file'
    TYPE_NAMES[InstanceType] = 'instance'
    TYPE_NAMES[LongType] = 'long int'
    TYPE_NAMES[SliceType] = 'slice'
    TYPE_NAMES[UnboundMethodType] = 'instance method'
    TYPE_NAMES[UnicodeType] = 'unicode',
    TYPE_NAMES[XRangeType] = 'xrange',
except NameError: pass


def get_type_name (some_type):
    try:
        return TYPE_NAMES[some_type]
    except KeyError:
        return some_type.__name__


class Dumper:

    def __init__ (self, max_depth=None, instance_dump=None, output=None):
        self._max_depth = max_depth
        self._instance_dump = instance_dump
        if output is None:
            self.out = sys.stdout
        else:
            self.out = output

    def __getattr__ (self, attr):
        if '_' + attr in self.__dict__:
            val = self.__dict__['_' + attr]
            if val is None:             # not defined in object;
                # attribute exists in instance (after adding _), but
                # not defined: get it from the module globals
                name_globals = vars(sys.modules[__name__])
                return name_globals.get(attr)
            else:
                # _ + attr exists and is defined (non-None)
                return val
        else:
            # _ + attr doesn't exist at all
            raise AttributeError(attr)


    def __setattr__ (self, attr, val):
        if '_' + attr in self.__dict__:
            self.__dict__['_' + attr] = val
        else:
            self.__dict__[attr] = val

    def _writeln (self, line):
        try:
            self.out.write(line.decode("utf-8"))
        except AttributeError:
            self.out.write(line) # python 3
        self.out.write(u"\n")
        
    def _write (self, text):
        try:
            self.out.write(text.decode("utf-8"))
        except AttributeError:
            self.out.write(text)

    def dump (self, val, indent='', summarize=1):
        self.seen = {}
        self.containing_instance = []
        self._dump (val, indent=indent, summarize=summarize)


    def _dump (self, val, depth=0, indent='', summarize=1):

        t = type (val)

        if short_value (val):
            self._write("%s%s" % (indent, short_dump (val)))

        else:
            depth = depth + 1

            if depth > self.max_depth:
                #raise SuppressedDump, "too deep"
                self._writeln(indent + "contents suppressed (too deep)")
                return

            if self.seen.get(id(val)):
                self._writeln(indent + "object already seen")
                return

            self.seen[id(val)] = 1

            if t in DICT_TYPES:
                if summarize:
                    self._writeln("%s%s:" % (indent, object_summary (val)))
                    indent = indent + '  '
                self.dump_dict (val, depth, indent)

            elif issubclass(t, (list, tuple)):
                if summarize:
                    self._writeln("%s%s:" % (indent, object_summary (val)))
                    indent = indent + '  '
                self.dump_sequence (val, depth, indent)

            elif is_instance(val):
                self.dump_instance (val, depth, indent, summarize)

            else:
                raise RuntimeError("this should not happen")

    # _dump ()


    def dump_dict (self, a_dict, depth, indent, shallow_attrs=()):
        keys = list(a_dict.keys())
        if type(keys) is type(list):
            keys.sort()

        for k in keys:
            val = a_dict[k]
            if short_value (val) or k in shallow_attrs:
                self._writeln("%s%s: %s" % (indent, k, short_dump (val)))
            else:
                self._writeln("%s%s: %s" % (indent, k, object_summary(val)))
                self._dump(val, depth, indent+'  ', summarize=0)


    def dump_sequence (self, seq, depth, indent):
        for i in range (len (seq)):
            val = seq[i]
            if short_value (val):
                self._writeln("%s%d: %s" % (indent, i, short_dump (val)))
            else:
                self._writeln("%s%d: %s" % (indent, i, object_summary(val)))
                self._dump(val, depth, indent+'  ', summarize=0)


    def dump_instance (self, inst, depth, indent, summarize=1):
        
        if summarize:
            self._writeln(indent + "%s " % object_summary (inst))
            indent = indent + '  '
        instance_dump = self.instance_dump

        # already dumping a containing instance, and have some restrictions
        # on instance-dumping?
        if self.containing_instance and instance_dump != 'all':

            previous_instance = self.containing_instance[-1]
            container_module = previous_instance.__class__.__module__
            container_package = (split (container_module, '.'))[0:-1]

            current_module = inst.__class__.__module__
            current_package = (split (current_module, '.'))[0:-1]

            #print "dumping instance contained in another instance %s:" % \
            #      previous_instance
            #print "  container module = %s" % container_module
            #print "  container package = %s" % container_package

            # inhibit dumping of all contained instances?
            if instance_dump == 'none':
                #raise SuppressedDump, "contained instance"
                self._writeln(
                    indent + "object contents suppressed (contained instance)")
                return

            # inhibit dumping instances from a different package?
            elif (instance_dump == 'package' and
                  current_package != container_package):
                #raise SuppressedDump, \
                #      "contained instance from different package"
                self._writeln(
                    indent + "object contents suppressed (instance from different package)")
                return

            # inhibit dumping instances from a different module?
            elif (instance_dump == 'module' and
                  current_module != container_module):
                #raise SuppressedDump, \
                #      "contained instance from different module"
                self._writeln(
                    indent + "object contents suppressed (instance from different module)")
                return

        # if in containing instance and have restrictions

        #self._writeln("")
        self.containing_instance.append (inst)
        shallow_attrs = getattr(inst, "_dump_shallow_attrs", [])
        self.dump_dict (vars (inst), depth, indent, shallow_attrs)
        del self.containing_instance[-1]


# end class Dumper


# -- Utility functions -------------------------------------------------

def atomic_type (t):
    return issubclass(t,
                      (None.__class__, float, complex)) \
                      or issubclass(t, integer_types) \
                      or issubclass(t, string_types)

def short_value (val):
    #if atomic_type (type (val)):
    #    return 1

    t = type(val)

    if (t not in DICT_TYPES and not isinstance(val, list) and
        not isinstance(val, tuple) and not is_instance(val)):
        return 1

    elif (isinstance(val, list) or isinstance(val, tuple)) and len (val) <= 10:
        for x in val:
            if not atomic_type (type (x)):
                return 0
        return 1

    elif t in DICT_TYPES and len (val) <= 5:
        for (k,v) in list(val.items()):
            if not (atomic_type (type (k)) and atomic_type (type (v))):
                return 0
        return 1

    else:
        return 0


def short_dump (val):
    if atomic_type(type(val)) or is_instance(val) or is_class(val):
        return repr(val)
    
    elif isinstance(val, (list, tuple)):
        if isinstance(val, list):
            retval = '['
        else:
            retval = '('
        if len(val):
            retval += short_dump(val[0])
            for item in val[1:]:
                retval += ", " + short_dump(item)
        if isinstance(val, list):
            retval += ']'
        else:
            retval += ')'
        
        return retval

    else:
        try:
            val = repr(val)
        except UnicodeError as err:
            val = "[got unicode error trying to represent value: " + str(err) +\
                ']'
        return object_summary (val) + ': ' + repr(val)
    
        

def object_summary (val):
    t = type (val)

    if is_instance(val):
        if hasattr(val, '__str__'):
            strform = ": " + str(val)
        else:
            strform = ""
        return "<%s at %x%s>" % (val.__class__.__name__, id (val), strform)

    elif is_class(val):
        return "<%s %s at 0x%x>" % (get_type_name(t), val.__name__, id (val))

    else:
        return "<%s at 0x%x>" % (get_type_name(t), id (val))
    

def is_instance (val):
    try:
        if type(val) is InstanceType:
            return 1
        # instance of extension class, but not an actual extension class
        elif (hasattr(val, '__class__') and
              hasattr(val, '__dict__') and
              not hasattr(val, '__bases__')):
            return 1
        else:
            return 0
    except NameError:  # Python > 3
        return (hasattr(val, '__class__') and \
              hasattr(val, '__dict__') and \
              not hasattr(val, '__bases__'))

def is_class (val):
    return hasattr(val, '__bases__')


default_dumper = Dumper()

def dump(val, output=None):
    if output is None:
        default_dumper.dump(val)
    else:
        Dumper(output=output).dump(val)

def dumps(val, *argv):
    from io import StringIO
    out = StringIO()
    dumper = Dumper(output=out)
    dumper.dump(val)
    for val in argv:
        dumper.dump(val)
    return out.getvalue()


if __name__ == "__main__":
    
    l1 = [3, 5, 'hello']
    t1 = ('uh', 'oh')
    l2 = ['foo', t1]
    d1 = {'k1': 'val1',
          'k2': l1,
          'k2': l2}

    print("a list: ", dumps (l1), "; a tuple: ", dumps (t1))
    print("a complex list: ")
    dump (l2)
    dump (d1)
    print("same dict, printed from dumps(): ")
    print(dumps(d1))
    dump (19)
    dump ("\nMy birth year!\n")

    dumper = Dumper (max_depth=1)
    l = ['foo', ['bar', 'baz', (1, 2, 3)]]
    dumper.dump (l)
    dumper.max_depth = 2
    dumper.dump (l)
    l[1][2] = tuple (range (11))
    dumper.dump (l)
    dumper.max_depth = None
    print(dumper.max_depth)
    
    class Foo: pass
    class Bar: pass

    f = Foo ()
    b = Bar ()

    f.a1 = 35
    f.a2 = l1
    f.a3 = l2
    f.b = b
    f.a4 = l2
    b.a1 = f
    b.a2 = None
    b.a3 = 'foo'

    dump (f)
