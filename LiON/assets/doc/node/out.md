NODE INFORMATION
    name: lion
    class: tree_conf
    category: system, out

DESCRIPTION
    Stores the result of each not-null returning calls.
    Useful for retreiving the result from the last call into another.

SYNTAX
    3 + 3
    echo ?out     # It will output 6


SAMPLE
    # Print numbers 1 to 100
    1
    repeat 100 {
        echo ?out
        ?out + 1
    }