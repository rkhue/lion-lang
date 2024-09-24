NODE INFORMATION
    name: call
    class: statement
    category: node_operations


DESCRIPTION
    A generic wrapper to the node operation `call`.
    Calls a given node by pathname with positional arguments and implicits.

SYNTAX
    <kw> call <pathname> <...> -> (a: b,) 

    -> <kw> meaning both scopes and restrictions

SAMPLES
    ```
    # Call all pathnames inside the tuple with arguments
    # Suppose functions `add` for addition, `sub` for subtraction
    # and `mul` for multiplication and `div` for division of two numbers

    var funcs (add, sub, mul, div)

    var n1 12
    var n2 4

    each f ?funcs {
        echo "Output of" ?f ": " [call ?f ?n1 ?n2]
    }

    ```