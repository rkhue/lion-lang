# JSON Intermediary Language for LiON .jill

## Overview
**JILL** is the intermediary representation language between the Higher Level Language (HL) and the complexities of the Runtime.

Since it's just JSON, it is meant be portable, readable and easily decompile(able) back to higher level with a **decompiler**.

### Process

The LXJ converts `code` from a raw UTF-8 string to a `json` that follows the JILL specification.

## DataTypes
In JILL, data is explicitly typed and represented as an JSON `array` of two elements `type` and `value`.

### Type literals
Scalars are types that are contained in themselves. Those in JILL are:

| Type      | Alias  | JSON               |
|-----------|--------|--------------------|
| None      | `none` | `["none", null]`   |
| Boolean   | `bool` | `["bool", true]`   |
| Integer   | `int`  | `["int", -2]`      |
| Floats    | `dec`  | `["dec", 3.14159]` |
| Strings   | `str`  | `["str", "jilly"]` |
| Reference | `ref`  | `["ref", 0]`       |

* For even more flexibility + independence, I'm thinking on adding a `bytes` type
but there still needs more thinking through it.

### Composite types
Those types, unlike literals, have other literals inside themselves. 

| Type    | Alias  | JSON            |
|---------|--------|-----------------|
| Code    | `code` | `["code", ...]` |
| Node    | `node` | `["node", ...]` |
| Clauses | `stmt` | `["stmt", ...]` |

For each composite type, a full section about their internals will be exposed in the document. For now, don't worry about them now.

## Calls & Code
Communication with the computer is made with `calls`

### Composition
JILL represents calls by:
1. `pathname` (what and where)
2. `posargs`: positional arguments (array of datatypes)
3. `kwargs`: keyword/implicit arguments  (ordered hashmap of arguments with defaults overridden).

* In JILL, a `call` would look something like this:
```json
{ 
    "pathname": "print",
    "posargs": [ 
        ["str", "hello"], 
        ["str", "world"] 
    ]
}
```
* To what would be in high level:
```
print hello world
```
### Call Structure
Currently, **calls in JILL are structured linearly**. Dependency is made by injecting `refs` into the call's positional arguments AND keyword arguments.


### Example
* Suppose the following code in HL (HL for Higher level):
```
print maths [+ 1 2]
```
* Calls breakdown

| `#` | Call            | Returns          |
|-----|-----------------|------------------|
| 0   | `+ 1 2`         | `["int", 3]`     |
| 1   | `print maths ~` | `["none", null]` |


* In a JILL `code` block
```json
[
    {
        "pathname": "+",
        "posargs": [
            ["int", 1],
            ["int", 2]
        ]
    },
    {
        "pathname": "print",
        "posargs": [
            ["str", "Basic"],
            ["str", "maths"],
            ["ref", 0]
        ]   
    }
]
```
* Notice that the second call _depends_ on the result of the first call to execute by having its third positional argument to _point_ to first call.

### Reference Counting
**IMPORTANT**: In JILL, you cannot reference a call's result more than once.

Every single time a dependency is _resolved_, that value must be freed from memory as to ensure safety. 

Thus, to ensure memory safety, each call can only be referenced **ONCE**.

**OBS:** Since the LXJ is the one who generates JILL from HL, it automatically goes through all this.


## Code Blocks
Code in JILL is just a JSON `array` of `call`s. Code can be passed as arguments, and stored as node data by the `code` datatype.


## Nodes
Nodes are represented in JILL as a JSON object. They're also first class citizens and can be passed as arguments / return via the `node` datatype. 

### Fields
Nodes in JILL are a JSON `object`, organized by the following fields:
* `name` : Name of the node
* `class`: NOP class of the node
* `rel`  : A JILL datatype, data held by the node
* `children`: Sub-nodes, allow for composition and more complex structures.

### Structures
#### Unit Node
The unit node is the simplest valid node, a dummy almost.  Only has a class as field structure.
```json
{
    "class": "unit"
}
```

#### Basic Node
A basic node has all the three base fields.
```json
{
    "name": "x",
    "class": "var",
    "rel": ["int", 10]
}
```
#### Anonymous Nodes
Those are nodes which do not have a `name`.
```json
{
    "class": "lambda",
    "rel": ["code", "..."]
}
```
* They are useful for representing anonymous functions, and other things which the `name` field does not make sense existing.

#### Composite Nodes
Composition allows for creating hierarchies of nodes. It is made via the `children` field.
```json
{
    "name": "Alex",
    "class": "Customer",
    "rel": ["int", 10],
    "children": {
        "wishlist": {
            "name": "wishlist",
            "class": "var",
            "rel": ["Apple", "Mango", "Jabuticaba"]
        }
    }
}
```
* Children are accessed by their `key`.

### Specifically classes.
As standardized by NOP, JILL considers the following system node classes:
- `reg`
- `variable`
- `lambda`
- `function`
- `overload`
- `template`
- `method`
- `trait`
- `class`

Every other class is a custom class, having the node point to its class' pathname.
The only caveat here is that you cannot serialize `builtin` nodes, since their relative, instead of pointing to a JILL datatype, they instead point to a implementation language's function. In the current case, Python or Rust.

## Node as First Class Citizens NFCC Model
Nodes can be passed as arguments and even be the return of a call via the `node` datatype, which stores a node as its value.
But currently, the LXJ cannot produce nodes directly as arguments, therefore, the node must come as the result of a `call` to be then passed.

### Base examples
See an example code block that adds a node to the tree:
```json
[
    {
        "pathname": "new",
        "posargs": [
            ["str", "node"],
            ["str", "fruit"],
            ["str", "var"],
            ["str", "apple"]
        ]
    },
    {
        "pathname": "pack",
        "posargs": [
            ["ref", 0]
        ]
    }
]
```
- OBS: Call 0 produces a new node as result, call 1 then uses the node.

Here's another example, now, it gets a node from the tree, then prints it:
```json
[
    {
        "pathname": "get",
        "posargs": [
          ["str", "mynode"]
        ]
    },
    {
        "pathname": "print",
        "posargs": [
          ["ref", 0]
        ]
    }
]
```

