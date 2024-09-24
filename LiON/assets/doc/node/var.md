NODE INFORMATION
    name: var
    class: def_constructor
    category: node, node_classes, variable-like

NODE CLASS INFORMATION
    %exec <*args> <*kwargs>
        return ?self.__rel__
    
    %new <pathname> <value>
        new node ?pathname variable ?value

DESCRIPTION
    The var constructor is used to create variables.
    All variables when called return the value passed to them, that is their relative.

SYNTAX
    var <pathname> <value>

    -> By default the `value` is none.

USAGE
    ```
    # Creating the variable
    var s 10
    var j (1, 2, 3)
    echo [?s + 1] [?s - 1]

    # Modifying the variable
    set s 2
    echo [?s + 1] [?s - 1]

    # Accessing elements from the relative
    # For more info use help __rel__
    echo [j 0] # 1
    ```