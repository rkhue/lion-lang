NODE INFORMATION
    name: function
    class: def_constructor
    category: node_classes, function, constructors

NODE CLASS INFORMATION
    %exec
        Create new local scope
        Add all __args__ to local scope
        Execute code in __rel__ in local scope

    %new (pathname, args)

DESCRIPTION
    Functions are used to execute and reuse code in the language.
    All functions when called, return the output of their code.

    Functions can have arguments passed to them, that is, some parameters
    become available in the function's scope for manipulation.

    All functions when ran, create a `this` pointer to the function that
    is running on the local scope. That is, we can use `this` to make more
    dynamic functions.

SYNTAX
    function <name> <code>
    -> Function without arguments

    function <name> <args> <code>
    -> Function with arguments

    function ... -> (**kwargs)
    -> We can pass attributes

SAMPLE
    - Simple 'Hello, World!'
        ```
        function hello {
            echo "Hello, World!"
        }
        hello
        ```
    - Simple addition function
        ```
        function add (x, y) {
            ?x + ?y
        }
        echo [add 1 2]
        echo [add 3 1]
        ```
    - Functions using `this`
        ```
        function domath (a, b) {
            ?a ?this.op ?b
        } -> (op: "+")
        ```