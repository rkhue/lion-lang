NODE INFORMATION
    name: alias
    class: def_constructor
    category: node, node_classes, alias-like, constructor

NODE CLASS BEHAVIOR:
    %exec <*args> -> (**kwargs)
        All aliases when executed call the pathname in their relative
    
    %new (pathname, pointer)
        new node ?pathname alias ?pointer
    
DESCRIPTION
    Constructor for creating nodes of the `alias` class.
    All aliases store a pathname in their relative (pointer), when called, the alias calls it's pointer.

SYNTAX
    alias <pathname> <pointer>

USAGE
    alias print echo
    print Hello, World!

    import @std/strman.py
    alias fmt str.format
    echo [fmt "Number: {:.2f}" 3.276777777]