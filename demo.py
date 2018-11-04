from app_error import AppLogger, AppStatus, AppError
#
# These are libraries that help implement the principles of effective logging:
#    https://techblog.chegg.com/#Logging
#
# AppLogger logs messages to include
#  * The name of the system generating the message (helpful in pipelines)
#  * The file name and line number where the log is written (helpful for quickly finding the relevant code)
#  * The log level of the message (useful for quick identification and filtering)
#  * The actual message
#  AppLogger allows you to specify the actual message as a list instead of a string, which makes it efficient enough
#   that you typically don't have to check the log level, and you can just call the log function blindly.  Example:
#  l = AppLogger('demo')
#  l.debug("This call won't build a big string from my list of numbers, ", [0, 1, 2, 3], " or serialize ",
#          my_complex_object, " unless debugging is turned on, so I can feel free to make lots of logging statements!")
#  if l.isSetDebug():
#      l.debug("I do want to protect logging inside conditional if I need to log with ", slow_function_call())
#
# AppStatus is like AppLogger, except it is a container for storing these various diagnostics, so they can be logged or
#   variously handled at higher levels in the call stack, providing for the principles of "effective logging".
#   It also provides a mechanism for passing computed values up the call stack, either individually, or multiple values
#   at once.  Think of it as a ledger to keep track of the things that happened so far in your program.
#   You don't have to make the hard choice of should I return a value, or should I throw an exception to indicate a 
#   special condition.  You can report everything and let the caller decide, but if they forget to explicitly ignore
#   errors, we'll still throw an exception.
#
# AppError is the same as AppStatus, but turned into an exception for those times when you really do want to throw an
#   exception.  But, included with the exception you can still have your ledger of computed value(s) and other 
#   diagnostics you collected up to the failure point, like warnings and info messages.
#   AppError doesn't inherit from AppStatus because AppStatus doesn't collect a stack trace, but AppError does.

# Basic usage - logger

l = AppLogger('demo')

l.error("I owe: $", 300 + 100, " dollars to my ex")
l.warn("I don't have enough money in the bank:  $", 0)
l.info("wise to pay your debts!")
l.debug("i probably shouldn't have borrowed gas money from her")
l.verbose = 2
l.v1("I borrowed $400")
l.v2("First it was $300")
l.v2("Then it was another $100")
l.v3("(It was to pay the rent)")
sample_output = '''
demo: ERROR: demo.py:35: I owe: $400 dollars to my ex
demo: WARN: demo.py:36: I don't have enough money in the bank:  $0
demo: INFO: demo.py:37: wise to pay your debts!
demo: DEBUG: demo.py:38: i probably shouldn't have borrowed gas money from her
demo: V1: demo.py:40: I borrowed $400
demo: V2: demo.py:41: First it was $300
demo: V2: demo.py:42: Then it was another $100
'''

# Basic usage - status

s = AppStatus()
if s.ok: l.info("we're doing fine")

s = AppStatus("unable to find boot sector")
s.addWarn("backup all data now")
if s.hasErrors(): l.error("We have a problem: ", str(s))  # shows whole status, inc. the warning
sample_output = '''
demo: INFO: demo.py:57: we're doing fine
demo: ERROR: demo.py:61: We have a problem: demo.py:59: unable to find boot sector; WARNINGS: demo.py:60: backup all data now
'''
# More fun with logger

## usage of verbose

def showVerbosity(l):
    l.ifverbose("ok, we're verbose!")
    l.ifverbose(2, "very verbose!")
    if l.verbose > 2:
        l.warn("we're too darned verbose!")

l = AppLogger('demo', verbose=2)   # can set in the constructor
showVerbosity(l)
l.v1("a verbose message")          # alternate syntax for creating log messages at different levels of verbosity
l.v2("a very verbose message")
l.v3("a very, very verbose message")
l.verbose = 1                      # property way to set
showVerbosity(l)
l.setVerbose(0)                    # equivalent way to set
showVerbosity(l)

## usage of debug

def showDebugLevel(l):
    l.ifdebug("we're debuggin!")
    l.ifdebug(5, " =? ", 2 + 3, tag="math")
    l.ifdebug("spelling is a breeze", tag='spelling')

l = AppLogger('demo', debug=True)  # can set in the constructor
showDebugLevel(l)
l.setDebug(False)                  # equivalent way to set
showDebugLevel(l)
l.setDebug('math')                 # can set to debug by tagname
showDebugLevel(l)
l.setDebug(['math', 'art'])        # or multiple tags

## getting log string instead of actually logging
for_later = l.info("I want to capture this log message for later", as_string=True)
l.info("Earlier I saw this message: ", for_later)

## log your log level
## I like to put this at the start of every program, so I can easily tell what log level the program ran at
l.announceMyself()  # can also be called with as_string=True parameter if you don't want to log immediately

# More fun with status object

## direct testing
if s: # same as if s.ok
    l.info("we're ok")

## dumping the status object
### shows all info, warnings, errors, and everything else in the status object, s
l.info(str(s))

## adding/removing info/warnings/errors to the status
s = AppStatus()
s.addInfo("threshold 1 was not met")
s.addInfo("threshold 2 was not met")
if s.hasInfo():
    l.info(s.getInfo())
    s.clearInfo()              # way to clear diagnostics 
s.addWarn("I think the wheels fell off")
if s.hasWarnings():
    l.warn(s.warnMsg())
    for warn in s.warnings:    # it's a list we can iterate
        if "the wheels fell off" in warn:
            s.addError(warn)   # will record this line number and line number of warning
    s.warnings = []            # We can also assign directly to the list, e.g. to clear
if s.hasErrors():
    l.error(s.errorMsg())      # N.B. l.error(s) would 

## adding a return value to status object (e.g. to pass it up the call stack along with the diagnostics)
s.addValue("foo")
try:
    l.info("got value '", s.getValue(), "'")
except AppError as err:
    l.warn(str(err))
    sample_output = '''
app_error.AppError: demo.py:138: You must clear errors on status object before accessing value: demo.py:131: demo.py:126: I think the wheels fell off; extra attributes: {'value': 'foo'}
'''
    s.clearErrors()
    l.info("got value '", s.getValue(), "'")  # now, no problem

## adding additional values to the status object
s.my_other_value = "bar"   # I can use any property name here
s.my_last_value = "last"
l.info("my status also has value ", s.my_other_value)

### getExtraAttrs() returns a dictionary with all the custom values as kv pairs (does not include s.getValue())
l.info("custom value: ", s.getExtraAttrs()["my_other_value"])

# deduping messages to remove clutter
for i in [1, 2]:
    s.addInfo("threshold 1 was not met")
s.dedupInfo()  # two messages about threshold 1 on same line become a single message with (x2) indicator
sample_output = '''

'''

## the "last_error"
### this is the last error added to the status
s = AppStatus("1. bad stuff happened")  # last_error = "1. bad stuff ..."
s.addError("2. the driver bailed")      # last_error  = "2. the driver ..."
current_status = AppStatus("3. the wheels fell off the bus")
s.addStatus(current_status)             # last_error = "3. the wheels ..."
if "the wheels fell off" in s.last_error:
    l.info("at the end of the day, the wheels fell off")
else:
    l.error("unexpected sequence of events; last error was: ", s.last_error)

## converting between status object and exception
s = AppStatus("the wheels fell off the bus")
try:
    # We can turn the status object to an AppError exception
    raise AppError(str(s))
    # Or we can directly create the AppError as easily as an AppStatus object
    raise AppError("Unexpectedly, we still have ", 4, " wheels")
except AppError as err:
    # we turn the exception back to a status object, e.g. to combine it with other status objects, etc.
    current_status = err.to_status()
    current_status.addWarn("Now we can do more with the status object")
    l.info(str(current_status))

## merging status objects together
### Handy to keep track of the cumulative outcome of multiple function calls
s1 = AppStatus().addInfo("Stuff is going well").addValue(1)
s2 = AppStatus("This time we blew it").addValue(2)
s2.foo = 'bar'  # extra attribute
### here we'll combine the info, error, and custom values set on both status objects, but when there are
###   conflicts, the last status object wins, so value will be 2
s1.addStatus(s2)
l.info(str(s1))
sample_output = '''
demo: INFO: demo.py:196: demo.py:191: This time we blew it; INFO: demo.py:190: Stuff is going well; extra attributes: {'value': 2, 'foo': 'bar'}
'''

## Logging all status levels at the appropriate log level
### The logger will create an INFO for each info entry in the status object, a WARN entry for each warn
###  etnry, etc.
s1.log(l)
### we can also prepend a custom message to each of those log lines
s1.log(l, "This is how it went down")
sample_output = '''
demo: ERROR: demo.py:206: This is how it went down: demo.py:191: This time we blew it
demo: INFO: demo.py:206: This is how it went down: demo.py:190: Stuff is going well
'''
    
# Advanced usage

## capture all log messages into a buffer
import io
buff = io.StringIO()
restore = l.diag_stream
l.diag_stream = buff
l.info("logging to a string now")
l.info("let's see what we got: ", l.diag_stream.getvalue())
l.diag_stream.close()
l.diag_stream = restore
l.info("logging normally again")

## easily set log levels from your commandline arguments
##   -- only works if you're using a "standard" commandline parser like docopt and you define 'debug' or 'verbose'
##   arguments, which will set 'debug'/'verbose' properties in your object or keys in a dict
from docopt import docopt
usage = '''
Usage: 
  demo [--verbose]... [--debug]
'''
args = docopt(usage, version='demo 1.0')
l.setFromArgs(args)
showVerbosity(l)  # will show how verbose we are, depending on which arguments were passed to demo

## logging a line from higher in the call stack
### When you have an error handler you don't want to put the file location of the handler in the log.  
###  Instead, you want to log the location where the error was detected.  All of the logger functions have 
###  the ability to specify higher stack frames to use when constructing the log message.
###  See this example:
def constructStatus(msg):
    # We return the string, instead of logging immediately because of as_string parameter
    return l.error("I'm deep in the error handler: ", msg, extra_frames=2, as_string=True)
def handleError(msg):
    # Maybe I want to send diagnostics somewhere other than the standard log file, or do other processing on errors,
    #  so I make an error handler
    deep_msg = constructStatus(msg)  # this is just for illustration
    # AppLogger functions accept the extra_frames parameter
    l.warn("I'm in the error handler: ", deep_msg, extra_frames=1)
handleError("Root problem is here")

## usage of numFramesInThisModule tells you how deep you are into the callstack for the current module
from app_error import numFramesInThisModule
def a():
    l.info("num frames deep in this module: ", numFramesInThisModule())
def b():
    a()
    l.info("num frames deep in this module: ", numFramesInThisModule())
def c():
    b()
    l.info("num frames deep in this module: ", numFramesInThisModule())
c()
sample_output = '''
demo: INFO: demo.py:136: num frames deep in this module: 4
demo: INFO: demo.py:139: num frames deep in this module: 3
demo: INFO: demo.py:142: num frames deep in this module: 2
'''