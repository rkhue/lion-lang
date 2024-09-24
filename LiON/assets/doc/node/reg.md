NODE INFORMATION
    name: reg
    class: tree_conf
    category: system, registry

DESCRIPTION
    The registry is used by LiON as a gateway to language critical nodes 
    such as classes, operators, exceptions and others. These kinds of nodes
    which need to be in the registry to be used by the language itself are
    known as `promotable` nodes.

    Here it is the usable domains and their relative promotables:
        - op -> operator / def_operator
        - except -> exception
        - classes -> class
        - locale -> locale
        - dms -> dms


SYNTAX
    To add a node to registry you may use the `promote` statement
    promote <pathname>

    To remove a node from the registry, you may use the `demote` statement
    demote <domain> <registry_key>

    To retrieve a node from registry, you may use:
    ?reg.<domain> >> <key>

    To display an registry domain, you may use any of the following:
    info reg.<domain>.__rel__

    linos reg.<domain>.__rel__

    display <domain>

SAMPLE
    - Consider the following operator
        ```
        operator mod (
            type: 2,
            proc: %,
            lam: [
                new lam (x, y) {
                    ?x % ?y
                }
            ]
        )
        ```
    - Now let's promote and use it
        ```
        promote mod
        
        echo [5 mod 10]

        ```

    - Now let's demote it
        ```
        demote op mod
        ```