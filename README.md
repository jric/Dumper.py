Dumper.py
=========

Code to dump out any Python object to text in a way that aids debugging /
useful logging.

    Dump Python data structures (including class instances) in a nicely-
    nested, easy-to-read form.  Handles recursive data structures properly,
    and has sensible options for limiting the extent of the dump both by
    simple depth and by some rules for how to handle contained instances.
    
    Copyright (c) 2009 Python Software Foundation
    Copyright (c) 2014 Joshua Richardson, Chegg Inc.
    
    Dumping is generally accessed through the 'dump()' function:
    
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

===

CHANGELOG:

1.2.0:  Added multi-argument support in dumps()
1.1.0:  Added more supported versions of python and a test framework.
1.0.4:  Fixed problem in Python 2 when using io.StringIO with dumper.
1.0.3:  Fixed problems in Python 3 related to trying to use decode as member of str.
1.0.2:  Include README.md and MANIFEST.in in the distribution.
1.0.1:  Include the package in the distribution.

