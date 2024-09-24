NODE INFORMATION
    name: maxi
    class: builtin
    category: iterable

DESCRIPTION
    Returns the last index of a given iterable
    That is their maximum accessible index

SYNTAX
    maxi <iterable>

USAGE
    var fruits (avocado, pineapple, caju, guaraná)
    
    each f_index [0 ~ [maxi ?fruits]] {
        echo Nº ?f_index : [fruits ?f_index]
    }