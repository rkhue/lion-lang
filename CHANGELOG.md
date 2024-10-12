<h1 style="text-align: center">
    LiON's Last Version Changelog (LLVC)
    <br>
    See what's new!
    <br>
</h1>
<i style="font-size: xx-large">
Overloaded functions, bugfixes 1.27
</i>
<br>

## Overlook ✨
### Additions
- Added `overload` functions that can redirect to other sub-functions by the number of arguments
- Added anonymous constructors, which do not require a pathname, instead they generate a hex uuid4
- Added `enum` for enumeration on iterables (1.27d)

### Documentation
- Added changelogs

### Improvements
- Made `lam` an anonymous constructor
- Added `multi-each` functionality to the `each` statement, that can combine with `enum` to create a more numeric approach to iterating. (1.27d)
- Made `set` statement NOT create new variables when not finding a pathname.

### Bugfixes
- At parser
  - Made constructing nodes with empty names not allowed
  - Made constructing non-string pathnames / names not allowed
  OBS: You can still do it with `conf`, but it will be fixed later
- At lexer
  - Comments took an extra character fixed (1.27c)

## References
* Go back to [Readme](README.md)
* See the [docs](LiON/assets/doc/liondoc.md)
* License: [GNU-GPLv3](LICENSE)
* GitHub: [LiON repository](https://www.github.com/rkhue/lion/)

Written 28-09-2024 by Felipe Fernandes

## About
LiON Copyright (C) 2024

> Changelog written in September 28th, 2024 (20-09-2024) 06:10 PM GMT-3
> 
> By Felipe Fernandes, the author. Profiled [rkhue](https://www.github.com/rkhue/) at GitHub
