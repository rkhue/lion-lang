NODE INFORMAITON
    name: each
    class: statement
    category: control-flow, conditioning

DESCRIPTION
    Used to execute blocks of code based on a condition.
    The cascade-if statement executes all valid conditions in it's if/elif clauses,
    if all of them are false, it defaults to the `else` clause if it exists.

    The `if` statement returns the output of the code it executes.

SYNTAX
    if <condition: bool> <code> ...
    if <condition: bool> <code> else <code>
    if <condition: bool> <code> elif <condition2: bool> <code>
    cascade if <condition> ...

    -> Clauses:
        - `elif` Executes when an above condition is false and it's condition is true.
        - `else` Executes when all conditions are false

     
SAMPLE
    - Simple case
    ```
    var coins 60
    var product 20

    if [?coins >= ?product] {
        echo "Can buy"
    } else {
        echo "Cannot buy"
    }
    ```

    - Using if's return
    ```
    # ...

    var status [
        if [?coins > ?product] {
            "Can buy"
        } else {
            "Cannot buy"
        }
    ]
    echo ?status
    ```

    - Cascade if sample
    ```
    var sequence "ABCDEF"

    cascade if ["A" in ?sequence] {
        echo "Found Armstrong"
    } elif ["DE" in ?sequence] {
        echo "Found Germany"
    } elif ["BR" in ?sequence] {
        echo "Found Brazil"
    } else {
        echo "Found nothing."
    }
    ```