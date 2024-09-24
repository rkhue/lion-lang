NODE INFORMAITON
    name: while
    class: statement
    category: control-flow, loops

DESCRIPTION
    Repeats a block of code until a given condition returns false.

SYNTAX
    while <condition> <code>

SAMPLE
    - Show all numbers from 1 to 10
        ```
        var cnt 1
        while {?cnt <= 10} {
            echo ?cnt
            ++ cnt
        }
        ```
    - Repeat until the user types a number
        ```
        var e none
        while {true} {
            set e [input "Enter something: "] 
            if [str.isnumeric ?e] {
                break        
            }
        }
        echo "Your number!" ?e
        ```