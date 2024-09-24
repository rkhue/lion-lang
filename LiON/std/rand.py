import random
global parent_parser, construct_builtin, construct_node

rand = construct_node("rand")

rand.update({
    "int": construct_builtin("int", random.randint),
    "obj": construct_builtin('obj', random.choice)
})

parent_parser.assign_references({
    "rand": rand
})

