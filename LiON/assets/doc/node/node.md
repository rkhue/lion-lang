NODE INFORMATION
    name: node
    class: def_constructor
    category: node, newable, constructors

NODE CLASS BEHAVIOR
    It's the simplest most node, does not have any behaviour other than being 
    able to be used with `new`

DESCRIPTION
    A constructor for a simple newable node.

    In Node Oriented Programming (NOP) a node is used as callable entities
    They are used to represent programming concepts such as variables, functions
    statements and anything really.
    
    In the simplemost level, all nodes are key-value pairs or dicts composed of
    three universal attributes:
        - __name__: 'Name of the node'
        - __class__: 'Defines the behaviour'
        - __rel__: 'Data'

    (More info on classes use `help class`)

SYNTAX
    node <pathname> <class> <relative>    

    -> By default:
        - `class` is 'newable'
        - `relative` is none
    
SAMPLE
    node flower variable "lilac"

    echo ?flower
    
    # Let's say I defined the class `Lion_` so that all nodes
    # from it when called print "Rawrr" to the screen
 
    node leo Lion_

    call leo   # "Rawrr"
