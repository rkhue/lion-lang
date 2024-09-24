NODE INFORMATION
    name: import
    class: statement
    category: system, import, plugins

DESCRIPTION
    Used to import .py plugins for LiON

SYNTAX
    import <filepath>

    import from <directory> (f1.py, f2.py, ....)

SAMPLE
    import @std/utils.py

    import from @std (
        utils.py,
        strman.py,
        rand.py
    )

SAMPLE PLUGIN
    - Code in python saved as `plugin.py`
        ```
        global parent_parser, construct_variable

        parent_parser.pack("foo", construct_variable("foo", "bar"))
        ```

    - Importing it
        import plugin.py

        echo ?foo