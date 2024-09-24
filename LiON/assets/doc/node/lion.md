NODE INFORMATION
    name: lion
    class: statement
    category: system, scripts, .lion file

DESCRIPTION
    Used for running code in .lion files.

SYNTAX
    lion <filepath>

    lion <filepath> -> (silent:<true/false>)

    -> silent if on removes the Finished message.

SAMPLE
    lion @samples/hello.lion

    lion @samples/times.lion -> (silent: true)
