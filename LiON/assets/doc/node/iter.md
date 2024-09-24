NODE INFORMAITON
    name: iter
    class: statement
    category: loops, iterable, comprehension

DESCRIPTION
    Used for list / iterable comprehension.
    It's used for building lists based on top of another
    iterable's elements.


SYNTAX
    iter <pathname> <iterable> <code>

SAMPLE
    - Generate a list with 10 even numbers
        ```
        var evens [iter x [1 ~ 10] {?x * 2}]
        echo ?evens
        ```
    - Convert a list of strings into a list of integers
        ```
        var nums_str [str.split [input "Type numbers > "]]
        
        var nums [iter n ?nums_str {cast.int ?n}]
        ```

    - Using `iter` with an if statement
        ```
        var nums [1 ~ 10]

        var states [
            iter n ?nums {
                if [?n % 2 == 0] {
                    "even"
                } else {
                    "odd"
                }
            }
        ]
        ```