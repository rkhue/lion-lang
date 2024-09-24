NODE INFORMAITON
    name: for
    class: statement
    category: control-flow, loops

DESCRIPTION
    Legacy for statement for a more controlled loop.
    It creates a node, then keeps running the loop code until the given
    condition is false, each iteration executing the increment.

    We use a constructor like `var` in the `start_code` for creating the node.

SYNTAX
    for <start_code> <condition> <increment> <code> 

SAMPLE
    ```
    # Show all powers of 2 up to 10
    for {var i 0} {?i <= 10} {++ i ?i} {
        echo ?i
    }
    ```