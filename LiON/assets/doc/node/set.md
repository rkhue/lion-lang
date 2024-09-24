NODE INFORMATION
    name: set
    class: statement
    category: node_operations, node, node_classes, variable-like

DESCRIPTION
    The `set` statement is used to modify the relative attribute from a node given it's pathname.
    If the given pathname does not exist, it will create a variable.

SYNTAX
    set <pathname> <value: Any>

    set <pathname>
    -> By default `value` is none

USAGE
    - Creating variables
        ```
        set n1 3
        set n2 4

        echo [?n1 * ?n2]
        ```

    - Modifying the relative
        ```
        function duck (a, b) { 
            ?a + ?b
        }
        echo [duck 4 6]   # 10

        # Changing duck to now multiply instead of sum
        set duck { ?a * ?b }

        echo [duck 4 6]   # 24
        ```