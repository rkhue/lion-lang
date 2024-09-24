# Welcome to LiON!
Here it is a cheatsheet for how to use it!
To see all documentation, type `__doc__` or [click here](liondoc.md)
### General Call Syntax:
```
<kw> <pathname> <arg1> <arg2> <...> -> (a:b, ...)
```
  - NOTE: `kw` can be both _scopes_ (`local` and `global`) and _restrictions_ (`protect`, `final`, `cascade` and `only`)

* All calls start with a pathname and the positional arguments are separated by spaces ` `
* The semicolon `;` is used for delimiting multiple calls.
* Implicit arguments are marked by an arrow `->` and a key-value pair after.
```lion
echo Hello, world!

echo Funny text -> (end: " indeed")
```

### Builtins:
* `echo` :Prints something to the screen: `echo Hello world!`
* `$`: Does arithmetic and logic:
  `$ 3 + 1`, `$ 3 < 9`, `$ 2 in 1 ~ 10`
* `linos`: List all nodes available:
  * You can pass a pathname to it, like `linos load` and it is going to list all children from `load`
* `info`: Prints a bulleted list of all nodes:
  `info ..name..`
* `tree`: Lists all children from the tree or a specified pathname
* `var`: Creates a variable:
    `var <name> <value>`
* `set`: Modifies a node's relative
     `set <pathname> <value>` 
* `input`: Retrieves user i/nput:
    `input <prompt>`
    `var username [input "What's your name? "]`

### Argument types:
* Strings `"x"`
* Integers `1`
* Floats or decimals `.3` `0.2` `1f` `1.3f`
* Percentage is marked by % at the end `3%` `.5%`
* Literals are marked with ? `?x`
* Square brackets [ ] are used to denote masks `[x]`
* Curly brackets { } denote blocks of code `{echo "hello world!"}`
* Parenthesis ( ) can be used:
  * For tuples: `(m, n, o)`
  * For key-value pairs: `(w: x, y: z)`
  * For arrays: `&(a, b, c, d)`

### Sample code
```
# Print the sum of two numbers
set x 12
set y 20

echo "x + y equals: " [$ ?x + ?y]
```
You can see more samples by going to [`@samples`](../../scripts/samples).