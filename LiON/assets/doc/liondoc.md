# Welcome to LiON!

LiON is a Node Oriented Scripting language that allows you for using it on shells and many other places!

## The Basics
This lovely section will explain the basics about LiON so you can get started with the language! 

To a faster cheatsheet, see [this file](help.md)
### What is a Node?
* Nodes are used in the language to represent everything programmable.
* They can store information, behaviour and much more.
* For now, see them as the things you use to well, _code_.

### What is a Call?
* In LiON, every instruction/statement is determined by a `call` to a **node**.
* Each call is at least composed by a `pathname`, that is, the name of the node you want to call.
* Calls can have positional arguments, or `posargs`, specified after the pathname and separated by empty spaces ' '
* At the end, a marker `->` is used for specifying implicit keyword arguments or `implicit` to the call.
* Each call is delimited either by a newline at the end or an semicolon `;`

#### Simple call Syntax
* Only pathname and posargs
```lion
<pathname> <arg1> <arg2> <...>

# Sample
echo Hello, World!
```
*Remember: Arguments are **always** separated by spaces!*
* With implicit keyword arguments.
```lion
<pathname> <...> -> (k: v, ...)

# Sample
printf "Cool text indeed " -> (end:" isn't it?")
```

* Multiple calls are delimited by semicolons (;) or newlines (\n)
```lion

echo I'm called; echo to say    # Two calls, one line, semicolon

echo that I love LiON
echo and I want to learn it     # Two calls, separated by newline at the end
```
### Understanding the "Hello, World!" program.
To print out "Hello World!" to the screen, we use the builtin node `echo` and pass the thing we want to print to it.
```lion
echo Hello, World!
```

### Strings
* A string is a `datatype` defined as a collection of characters.
* By default, everything non-recognized in LiON is defined as an `unk` string.
* Or, if you want them to be explicit `str`, you enclose your block of text in double quotes, like this `"text block with spaces"`

```lion
echo "I'm a block of text!" 
```
  - Note that this counts as _one argument_ passed to `echo`.
```
echo I'm a block of text!
```
  - While this is considered to be 5 arguments.

#### So why `echo` still works even if I don't use strings?
Well, the `echo` builtin can receive _n_ arguments, that is, an unlimited amount of arguments.
Then, it joins all arguments using an empty space as divisor, then prints to screen.

> Best practice is to just put double quotes when you are unsure `:)`

### Variables
* In LiON, variables are nodes from the class `variable`, that when called, return their data. * They can be created by using the `var` constructor.
```lion
var x 10
```
  - In this case, we created a variable at pathname `x` with its relative being the number "10"

* To access the value of `x`, we simply call it:
```lion
x
```

* Now to modify any variable, we use the `set` builtin.
```
set x 20
```

### Literals
Given as arguments and marked by `?`, `literals` are used to get the *relative value* of any node by its pathname and put it in the place of the literal.
See down an example:
```
# Set an variable x:
var x 37
#Print `x` using a literal:
echo The value of X is ?x
```

### Masks
Given as arguments to a call, `masks` serve to put the output of a call in the mask's place. They are marked by brackets `[ ]`.
See down an example usage:
```lion
var x 10
echo "The value of x is" [x]
```
** *Note: since variables return their relatives when called, `[x]` will put 10 at the mask's place*
Now, see a more detailed example:
```lion
var x 10
echo "X + 10 is: " [$ ?x + 10]
```
** *In this case, we used both literals and masks. And the `$` builtin for doing arithmetic and logic, more on `$` later*

### Using masks for user input
In LiON, we have a builtin called `input`, that receives a prompt as argument and returns the text typed by the user.
Let's say I want to print out a user's favourite fruit:
```lion
# Get user input
var preference [input "What's your favourite fruit? "]
echo "You like" ?preference
```

### The builtin `$`, logic and arithmetic
In LiON, the builtin node `$` is responsible for handling arithmetic, logic and set operations.
After called, it returns the result of the given expression.
To see the list of operators [click here](operators.md)

### Codeblocks and Labels
Codeblocks are a primitive type to store code, although simple, codeblocks can be stored inside a node's relative.
Nodes which have code as relatives, are classified as labels.
To make a label, we can use the following code:
```lion
# The `label` statement allows for simple creation
var foo {
    echo I <3 LiON!
}
```
#### Using the `do` statement
The `do` statement is used to execute codeblocks. See down an example:
```lion
do {
    echo Hello world!
}
```
Labels, when called, return their relatives, so we can use the `do` statement to execute them:
```lion
# Create and execute labels
var lobby {
    echo "Welcome to the lobby!"
}
do ?lobby
```
### Control flow statements
#### The `if` statement
The if statement executes a code block if a given condition is true.
```lion
if [condition] {
    # code to be executed
}
```
- The `else` clause permits for you executing code if the given condition is false.
```
var fruit "banana"
if [?fruit == "apple"] {
    echo "It is an apple"
} else { 
    echo "Not an apple"
}
```
- The `elif` clause allows to specify a new condition if the first condition is false.
```
var coins 100
var product_price 329
if [?coins > ?product_price] {
    echo "You can buy"
} elif [?coins == ?product_price] {
    echo "You can buy, but you'll have no coins left."
} else {
    echo "Cannot buy"
}
```
#### The `cascade-if` statement
```lion

```
#### The `switch` statement

#### The `repeat` statement
#### The `do-repeat` statement

#### The `while` statement
#### The `do-while` statement

#### The `each` statement
#### The `for` statement

### Repetition auxiliaries

### Functions

### 