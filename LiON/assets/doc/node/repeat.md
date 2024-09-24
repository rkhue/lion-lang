NODE INFORMAITON
    name: repeat
    class: statement
    category: control-flow, loops

DESCRIPTION
    Repeats a given block of code a fixed amount of times.

SYNTAX
    repeat <amount> <code>

    repeat (<pathname>, <amount>) <code>

    -> Creates a variable to keep track of the current
       iteration.

SAMPLE
    - Simple repetition
        ```
        repeat 10 {
            echo Pizza! Yum
        }
        ```
    - Counting repetition
        ```
        # Check if all numbers from 0 to 9 are divisible by 4
        repeat (i, 10) {
            echo ?i is [if [?i % 4 == 0] {"yes"} else {"no"}]
        }
        ```
