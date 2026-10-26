import random
global parent_parser, construct_builtin, construct_node

rand = construct_node("rand")

def shuffle(*args):
    if not args:
        raise ValueError("Cannot shuffle an empty list of arguments.")

    args = list(args)
    random.shuffle(args)
    return args

rand.update({
    "int": construct_builtin("int", random.randint),
    "obj": construct_builtin('obj', random.choice),
    "shuffle": construct_builtin('shuffle', shuffle),
    "float": construct_builtin('float', random.uniform)
})

parent_parser.assign_references({
    "rand": rand
})

