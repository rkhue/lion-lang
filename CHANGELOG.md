<h1 style="text-align: center">
    LiON's Last Version Changelog (LLVC)
    <br>
    See what's new!
    <br>
</h1>
<i style="font-size: xx-large">
Function masks, more functional features, optimized lexer, 1.28a
</i>
<br>

## Overlook ✨
### Additions
- Added from Python:
  - `avg` for getting the average of all numbers in a given iterable
  - `sum` for getting the sum of all numbers in a given iterable
  - `any` checks if any element of a given iterable is true
  - `all` checks if all elements of a given iterable are true

- Add `reduce` for folding an iterable's elements by a given node
- Add `curry.lion` script at `@scripts` for demonstrating some currying with functions.
- Add `curry` constructor in `@std/construtil.lion` for facilitating currying.
- Added function masks, that is a new way of calling functions in LiON that's more aligned with other programming languages.
  - Example: 
    ```sh
    function add (x, y) {?x + ?y}
    # traditional mask
    echo [add 1 2]
    
    # function mask
    echo add[1 2]      # syntax: <pathname>[arg1 arg2 ...]
    ```
  - Explanation: Both calls are equivalent and produce the same result, we can pass the pathname to be before the arguments, which are enclosed by `[ ]`
  - For now, function masks _do not_ work with nodes whose pathnames are not alphanumeric.
  > **NOTICE:** This is an _experimental_ feature, it's not final and can change/be-removed over the course of time.


### Improvements
- Made `exec` receive an exact amount of arguments.
- Made `lam`, `function` and `saber` constructors allow kwargs so for currying.
- Made the categorizer from lexer optimize single masks in a call. So adding multiple nested masks don't compromise too much performance.

## References
* Go back to [Readme](README.md)
* See the [docs](LiON/assets/doc/liondoc.md)
* License: [GNU-GPLv3](LICENSE)
* GitHub: [LiON repository](https://www.github.com/rkhue/lion/)

Written 13-10-2024 by Felipe Fernandes

## About
LiON Copyright (C) 2024

> Changelog written in October 13th, 2024 (13-10-2024) 22:30 GMT-3
> 
> By Felipe Fernandes, the author. Profiled [rkhue](https://www.github.com/rkhue/) at GitHub
