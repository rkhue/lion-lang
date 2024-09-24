NODE INFORMAITON
    name: itert
    class: statement
    category: loops, iterable, comprehension

DESCRIPTION
    Used for iterable comprehension.
    Same as `iter`, instead it returns the result as a tuple.


SYNTAX
    itert <pathname> <iterable> <code>

SAMPLE
    ```
    var squares [itert x [1 ~ 10] {?x ** 2}]

    echo ?squares
    ```