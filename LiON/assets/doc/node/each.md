NODE INFORMAITON
    name: each
    class: statement
    category: control-flow, loops

DESCRIPTION
    Used to iterate over the elements of tuples, lists and strings.

SYNTAX
    each <pathname> <iterable> <code>

SAMPLE
    - Show numbers from 1 to 10
        ```
        each number [1 ~ 10] {
            echo ?number
        }
        ```
    - Display all letters from the alphabet, indexed
        ```
        var i 1
        each letter ?str.alphabet {
            echo - ?i : ?letter
            ++ i
        }
        ```