NODE INFORMATION
    name: set
    class: statement
    category: node_operations, node, node_classes, variable-like

DESCRIPTION
    The `set` statement is used to modify the relative attribute from a node given it's pathname.

SYNTAX
    set <pathname> <value: Any>

    set <pathname>
    -> By default `value` is none

USAGE
    - Modifying variables
        ```
        var health 200
        echo Your health is ?health
        set health 100
        echo After an attack, it's now ?health
        ```

    - Modifying the relative of any node
        ```
        function duck (a, b) { 
            ?a + ?b
        }
        echo [duck 4 6]   # 10

        # Changing duck to now multiply instead of sum
        set duck { ?a * ?b }

        echo [duck 4 6]   # 24
        ```