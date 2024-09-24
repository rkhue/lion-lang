NODE INFORMATION
    name: do
    class: statement
    category: code_execution, control-flow, loops

DESCRIPTION
    This statement is used for executing blocks of code.
    Some clauses are also used with do:
        - while:
        Execute a codeblock, repeat while a condition is true.

        - repeat
        Execute a codeblock, repeat then a fixed amount of times.
    
SYNTAX
    do <code>
    do <code> while <condition>
    do <code> repeat <condition>

USAGE
    - Directly executing a codeblock
        ```
        do {
            echo "Hello, World!"
        }
        ```
    - Executing a label
        ```
        var food { echo "Spaghetti" }

        do ?food
        ```

    - Showing numbers 1 to 10 using do-while
        ```
        var count 1
        do {
            echo ?count
            ++ 
        }
        ```