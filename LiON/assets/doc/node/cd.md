NODE INFORMATION
    name: cd
    class: builtin
    category: directory, file system, LSI


DESCRIPTION
    Used to change from directory A to B in the LSI

SYNTAX
    cd <filepath>
    -> The filepath can be having DMS symbols

SAMPLES
    - Changing to a directory with dms symbol
        ```
        cd @u/LiONProjects/my_proj
        ```
    - Changing to some directory
        ```
        cd ./downloads/
        ```