# LiON Architecture & Implementation Specification

**Repository:** `rkhue/lion-lang`  
**Analyzed implementation:** Python runtime, shell, CLI, standard library, and packaged assets  
**Purpose:** Baseline source of truth for a future Python-to-Rust runtime migration

## 1. Executive Summary & System Overview

LiON is a node-oriented programming language. The implementation does not build a traditional AST and does not execute bytecode. It has two representations:

1. Source text is split and type-condemned by [`LiON/lexer.py`](./LiON/lexer.py) into a list of call dictionaries.
2. The call dictionaries are interpreted by [`TreeManager`](./LiON/parser.py) against a mutable hierarchical node tree. The same representation can be serialized as JSON (`lionc.py -c`) and later loaded by `lionc.py -exec`.

The central runtime object is [`LiONStandard`](./LiON/__init__.py), which extends [`LiONBasic`](./LiON/basic.py), which extends [`TreeManager`](./LiON/parser.py), which extends [`Scope`](./LiON/scope.py). Runtime services (DMS, operators, language semantics, standard functions, and optional modules) populate the root tree during setup.

```text
                         +----------------------+
 python console.py ----> | LiON_shell.LSI       |
 python main.py -------> | prompt_toolkit REPL  |
                         +----------+-----------+
                                    |
                         prompt / multiline input
                                    v
 +----------------+       +--------+---------+       +-------------------+
 | lionc.py       | ----> | LiON.shell.start | ----> | LiONStandard      |
 | -r/-i/-wi/-sh  |       | basic REPL       |       | setup + root tree |
 | -c/-exec/-h    |       +--------+---------+       +---------+---------+
 +--------+-------+                |                           |
          |                        | source text              |
          |                        v                           v
          |                 +------+-------+           +-------+--------+
          |                 | full_lexer  |           | parse_calls /  |
          |                 | delimiter   |           | parse_call     |
          |                 | tokenizer   |           +-------+--------+
          |                 | condemner   |                   |
          |                 +------+-------+                   v
          |                        |                  +--------+--------+
          |                        | call dicts       | TreeManager     |
          |                        +----------------> | get/exec/new/  |
          |                                           | pack/scopes     |
          |                                           +---+---------+---+
          |                                               |
          |                         +---------------------+-------------------+
          |                         |                     |                   |
          v                         v                     v                   v
      JSON file             node tree/registry       Python built-ins      OS/files
      (LiON C.F.)            scopes/closures          std modules           DMS
```

### Design philosophies and assumptions

- **Nodes are the universal abstraction.** Variables, functions, methods, constructors, classes, operators, exceptions, registries, scopes, aliases, and locale data are dictionaries identified by `__name__`, `__class__`, and `__rel__`.
- **The root is a mutable object graph.** Names are usually addressed by dot-separated pathnames such as `math.sin` or `reg.classes`.
- **Behavior is registry-driven.** `LiONBasic.setup()` installs cargo and promotes classes/operators/locales into registries.
- **Language syntax is extensible through locale aliases.** `LanguageManager` maps semantic keywords to aliases and can add/remove language definitions at runtime.
- **Python interoperability is intentional.** Builtins hold Python callables directly; `import` can execute Python source with an injected runtime namespace.
- **Interactive and file execution share one interpreter.** A REPL keeps the initialized root and scopes alive; `run_statement` parses code into that same tree.
- **Errors are mostly Python exceptions.** LiON-specific subclasses provide semantic categories, but many invalid states still surface as `AssertionError`, `KeyError`, `TypeError`, or other native exceptions.
- **Security is advisory, not a sandbox.** `secure` and restriction markers protect selected nodes, but the runtime exposes Python execution, imports, subprocesses, filesystem access, and `os.system`.

## 2. Module & Directory Map

### 2.1 Entry points and project metadata

| Path | Responsibility |
|---|---|
| [`lionc.py`](./lionc.py) | Command dispatcher; source execution, JSON compilation, JSON execution, shell selection, help, importable `lionc` node. |
| [`main.py`](./main.py) | Minimal launcher calling `LiON.shell.start()`. |
| [`console.py`](./console.py) | Launcher constructing `LiON_shell.LSI` and running it with initialization. |
| [`console.cmd`](./console.cmd) | Windows launcher: `py console.py`. |
| [`console.sh`](./console.sh) | POSIX launcher: `python3 console.py`. |
| [`requirements.txt`](./requirements.txt) | `tqdm`, `pygments`, `prompt_toolkit`, `PyYAML`. |
| [`README.md`](./README.md) | User-facing installation and introductory behavior. |
| [`CHANGELOG.md`](./CHANGELOG.md) | Release/change history. |
| [`jill-spec.md`](./jill-spec.md) | Jill-related language/specification material. |
| [`LICENSE`](./LICENSE) | GPLv3 license. |
| `.gitignore` and `.idea/` | Ignore rules and IDE metadata; not runtime dependencies. |

### 2.2 Core runtime package

| Path | Responsibility and important symbols |
|---|---|
| [`LiON/__init__.py`](./LiON/__init__.py) | Defines `LiONStandard`; standard cargo, reset/repair, diagnostics, printing, timing, tree visualization, and high-level modules. |
| [`LiON/basic.py`](./LiON/basic.py) | Defines `LiONBasic`; setup, registries, builtins/statements/constructors, Python execution, control flow, functions/classes, I/O, operators, and semantic statements. |
| [`LiON/parser.py`](./LiON/parser.py) | Defines `TreeManager`; node lookup/mutation, construction, execution dispatch, parsing call dictionaries, scope-aware execution. |
| [`LiON/scope.py`](./LiON/scope.py) | Defines `Scope`, `scoped`, `rel_modify`, `rel_retrieve`; stacked dictionaries, path resolution, restrictions, and relative operations. |
| [`LiON/lion_node.py`](./LiON/lion_node.py) | Node predicates and constructors: `construct_node`, `construct_variable`, `construct_function`, `construct_class`-style helpers, registries, locales, exceptions, and root tree creation. |
| [`LiON/lexer.py`](./LiON/lexer.py) | Source lexer: delimiter splitting, tokenization, type condemning, marker categorization, nested masks, collections, comments, and JSON output. |
| [`LiON/exceptions.py`](./LiON/exceptions.py) | `LiONException` and lexical, parsing, node, registry, DMS, class, binding, and flipping error subclasses. |
| [`LiON/funclib.py`](./LiON/funclib.py) | General Python helpers: file/JSON/text I/O, paths, colors, prompts, matrix/math helpers, permissions, cache cleanup, zipping, and miscellaneous utilities. |
| [`LiON/shell.py`](./LiON/shell.py) | Basic stdin REPL, prompt, bracket continuation, `!` shell commands, output formatting, initialization, and exception display. |

### 2.3 Language definition modules

| Path | Responsibility |
|---|---|
| [`LiON/lang/const.py`](./LiON/lang/const.py) | Node class names, node attribute keys, registries, execution markers, root configuration names, and class sets. |
| [`LiON/lang/lexerconst.py`](./LiON/lang/lexerconst.py) | Lexical markers, bracket/comment rules, scope keywords, token type names, boolean/null literals, pathname markers, and regexes. |
| [`LiON/lang/semantic.py`](./LiON/lang/semantic.py) | Canonical semantic keyword constants and `KEYWORD_DICTIONARY`. |
| [`LiON/lang/control.py`](./LiON/lang/control.py) | `AbstractInternal` and `AB_CALLS` for `break`/`continue` propagation. |
| [`LiON/lang/restrictions.py`](./LiON/lang/restrictions.py) | Restriction names: `only`, `final`, `protect`, `cascade`, `static`. |

### 2.4 Runtime modules

| Path | Responsibility |
|---|---|
| [`LiON/modules/dms/__init__.py`](./LiON/modules/dms/__init__.py) | `LionDMS`: symbolic directories (`@`, `%`, `~`), cwd/home, path translation, directory changes/listing. |
| [`LiON/modules/opman/__init__.py`](./LiON/modules/opman/__init__.py) | `OperatorManager`: operator registry access, unary/binary dispatch, shunting-yard conversion, postfix evaluation. |
| [`LiON/modules/opman/operators.py`](./LiON/modules/opman/operators.py) | Built-in arithmetic, collection, relational, logical, interval, scaling, and node operators. |
| [`LiON/modules/lman/__init__.py`](./LiON/modules/lman/__init__.py) | `LanguageManager`: locale registry, semantic lookup, alias installation/removal, locale JSON loading. |
| [`LiON/modules/lml/compile.py`](./LiON/modules/lml/compile.py) | `LMLCompiler`: converts text blocks, `@@` directives, and `@{...}@` LiON code blocks into `lmout` calls. |
| [`LiON/modules/lml/const.py`](./LiON/modules/lml/const.py) | LML marker and temporary-name constants. |
| [`LiON/modules/neo/style.py`](./LiON/modules/neo/style.py) | `NeoStyleSheet`: YAML style loading, ANSI compilation, embedded colors, caching, rendering. |
| [`LiON/modules/neo/const.py`](./LiON/modules/neo/const.py) | ANSI parameter and special color definitions. |
| [`LiON/modules/treevisu/__init__.py`](./LiON/modules/treevisu/__init__.py) | Tree visualization helpers, emoji/color selection, node analysis. |
| [`LiON/modules/treevisu/theme.py`](./LiON/modules/treevisu/theme.py) | Tree visualization theme data. |
| `LiON/modules/*/__init__.py` | Package markers; the `dms`, `lman`, `opman`, `lml`, `neo`, and `treevisu` packages contain the active modules above. |

### 2.5 Standard library and extension scripts

| Path | Responsibility |
|---|---|
| [`LiON/std/lcast.py`](./LiON/std/lcast.py) | Cast-related standard extension hook. |
| [`LiON/std/lfutil.py`](./LiON/std/lfutil.py) | Functional helpers, including reduction-related utilities. |
| [`LiON/std/lmath.py`](./LiON/std/lmath.py) | Math node with constants, predicates, trigonometry, logarithms, and `delta`/`bhask`/`vertex`. |
| [`LiON/std/lml.py`](./LiON/std/lml.py) | LiON-facing LML compile/run nodes and mode validation. |
| [`LiON/std/lorem.py`](./LiON/std/lorem.py) | Random lorem/text helpers. |
| [`LiON/std/lsh.py`](./LiON/std/lsh.py) | `sh`, subprocess, and process-module integration. |
| [`LiON/std/ltime.py`](./LiON/std/ltime.py) | `current`, `timeit`, and threaded `timeout`. |
| [`LiON/std/neo.py`](./LiON/std/neo.py) | `neo` stylesheet and `aquarela` output nodes. |
| [`LiON/std/rand.py`](./LiON/std/rand.py) | Random helpers. |
| [`LiON/std/strman.py`](./LiON/std/strman.py) | String manipulation helpers. |
| [`LiON/std/utils.py`](./LiON/std/utils.py) | JSON/OS utility helpers. |
| [`LiON/std/construtil.lion`](./LiON/std/construtil.lion) | LiON-level constructor utilities. |
| [`LiON/std/ps.lion`](./LiON/std/ps.lion) | LiON-level process/script support. |
| [`LiON/std/fact.json`](./LiON/std/fact.json) | JSON data consumed by standard features. |
| `LiON/std/__init__.py` | Standard-library package marker. |

### 2.6 Enhanced shell

| Path | Responsibility |
|---|---|
| [`LiON_shell/__init__.py`](./LiON_shell/__init__.py) | `LSI`, the prompt-toolkit shell with history, completion, syntax highlighting, toolbar, multiline prompts, init scripts, and error handling. |
| [`LiON_shell/lexman.py`](./LiON_shell/lexman.py) | Pygments `LiONLexer` for syntax highlighting; keyword, operator, literal, punctuation, and string rules. |
| [`LiON_shell/shellinit.lion`](./LiON_shell/shellinit.lion) | Shell initialization code. |
| [`LiON_shell/docs/lionc_help.md`](./LiON_shell/docs/lionc_help.md) | `lionc.py` command help loaded at import time. |
| [`LiON_shell/icon/icons.json`](./LiON_shell/icon/icons.json) | Shell/icon metadata. |

### 2.7 Assets and sample programs

- `LiON/assets/conf/notice.txt` and `verinfo.json`: license/notice and version metadata.
- `LiON/assets/doc/index.md`, `help.md`, `liondoc.md`, and `operators.md`: language and operator documentation.
- `LiON/assets/doc/node/`: the complete node reference set: `!.md`, `$.md`, `++.md`, `--.md`, `DOC_DIR.md`, `alias.md`, `anl.md`, `assert.md`, `bench.md`, `cache.md`, `call.md`, `cast.md`, `cat.md`, `cd.md`, `class.md`, `clear.md`, `colsim.md`, `conf.md`, `constructor.md`, `current.md`, `cwd.md`, `debug.md`, `del.md`, `demote.md`, `dir.md`, `display.md`, `dms.md`, `do.md`, `drop.md`, `each.md`, `echo.md`, `equals.md`, `exception.md`, `exec.md`, `export.md`, `extend.md`, `file.md`, `filter.md`, `flip.md`, `for.md`, `function.md`, `genmd.md`, `get.md`, `get_std.md`, `help.md`, `highlight.md`, `if.md`, `import.md`, `info.md`, `inherited.md`, `input.md`, `is_op.md`, `iter.md`, `iters.md`, `itert.md`, `json.md`, `keysfrom.md`, `keyvalue.md`, `lam.md`, `lang.md`, `len.md`, `lex.md`, `linos.md`, `lion.md`, `list.md`, `load.md`, `ls.md`, `maxi.md`, `merge.md`, `method.md`, `mkdir.md`, `move.md`, `new.md`, `node.md`, `notice.md`, `operator.md`, `out.md`, `pack.md`, `pop.md`, `printf.md`, `promote.md`, `push.md`, `quote.md`, `range.md`, `recho.md`, `reg.md`, `rename.md`, `repair.md`, `repeat.md`, `reset.md`, `return.md`, `rm.md`, `saber.md`, `scopes.md`, `see.md`, `seef.md`, `set.md`, `sh.md`, `shell.md`, `stdout.md`, `string.md`, `struct.md`, `switch.md`, `throw.md`, `throw_err.md`, `timeit.md`, `timeout.md`, `touch.md`, `tree.md`, `try.md`, `tuple.md`, `var.md`, `version.md`, `while.md`, and `write.md`. These are runtime-discovered by `LiONBasic.get_docs()`.
- `LiON/assets/locale/en-us.json` and `pt-br.json`: locale data.
- `LiON/assets/theme/color.css`: theme data.
- `LiON/assets/img/icon/blue-favicon.png`, `blue-large.png`, `red-favicon.png`, `red-large.png`, and `assets/img/readme/screenshot-lsi.png`: visual assets only.
- `LiON/scripts/init.lion`, `repl.lion`, `benchmark.lion`, and `genlog.lion`: startup, REPL, benchmark, and log-generation scripts.
- `LiON/scripts/samples/`: `10evens.lion`, `binary-tree.lion`, `bolt.lion`, `button.lion`, `class.lion`, `classroom.lion`, `counter.lion`, `curry.lion`, `dialogue.lion`, `except.lion`, `for.lion`, `func-nesting.lion`, `hello.lion`, `kill_tree.lion`, `lights.lion`, `op.lion`, `overload.lion`, `person.lion`, `person.lions`, `ping.lion`, `santi.lion`, `struct.lion`, and `times.lion`; executable examples and regression-by-example material.

## 3. Detailed Component Breakdown

### 3.1 CLI interface and entry points

#### Argument parsing

[`lionc.py`](./lionc.py) uses a custom positional dispatcher, not `argparse`, `click`, or `typer`. `parse_argv(*args)` removes `argv[0]` unless imported through the LiON runtime (`LOADED_FROM_IMPORT`), lowercases the first argument, and matches:

| Command | Behavior | Validation and result |
|---|---|---|
| `-r <filepath>` | `lion.run_statement(path)` | Existing regular file; catches `OSError`/`UnicodeError`; returns `2` on error. |
| `-sh` | Basic `LiON.shell.start()` REPL | No arguments. |
| `-wi` | `LSI().run(False)` | Enhanced shell without shell-init script. |
| `-i` | `LSI().run()` | Enhanced shell with shell-init script. |
| `-c <input> <output> [--d\|--debug]` | Lexes source, wraps it with `construct_variable(filename.name, lexed_code)`, serializes JSON, atomically writes output | Rejects unknown optional flags, same input/output, missing files/directories; catches OS, Unicode, type, and value errors. |
| `-exec <input_filepath>` | Loads JSON, calls `lion.exec(node)`, formats result, prints completion | Catches OS, Unicode, JSON, type, and value errors. |
| `-h` | Prints `LiON_shell/docs/lionc_help.md` | No arguments. |
| anything else | Error message | Exit result `2`. |

`_path_argument()` expands `~`, resolves required inputs strictly, requires regular files, and checks output parent directories. `_write_compiled()` writes to `.<name>.<pid>.tmp` with exclusive creation and replaces the destination using `os.replace`; its cleanup only unlinks the temporary file if creation succeeded.

#### Invocation lifecycle

1. Importing `LiON` constructs no runtime until `lionc.py` chooses `LiONStandard()`; importing `lionc.py` from LiON code instead discovers an injected `parent_parser` and registers a `lionc` node.
2. `LiONStandard()` constructs the root and service managers, then calls `setup()`.
3. `setup()` installs version/notice data, standard operators, DMS/language-manager cargo, standard cargo, locale aliases, and recursive `protect` restrictions.
4. `-r` reads and parses source in the initialized root; `-c` only lexes and emits JSON; `-exec` loads a serialized node and dispatches it.
5. `__main__` calls `sys.exit(parse_argv(*sys.argv))`. Success is `0`; usage/input failures are `2`. Shell exceptions are handled inside their shell loops and generally do not become CLI exit statuses.

#### Configuration and environment

- No environment variable or configuration file is parsed as a CLI configuration layer.
- Current working directory (`os.getcwd()`), user home (`Path.home()`), and module directory (`os.path.dirname(__file__)`) seed DMS symbols.
- `LiON/assets/conf/verinfo.json`, `notice.txt`, locale JSON, YAML style properties, and shell initialization files are runtime resources.
- Python import execution receives `__filename__`, `__home__`, `root`, `dms`, `lman`, `opman`, I/O functions, and constructors.
- `PATH` is affected by `sys.path.append()` in `execute_python`; the code also appends `LiON/std/` using a string that appears to rely on path concatenation.

### 3.2 Basic interactive shell

[`LiON/shell.py`](./LiON/shell.py) creates a module-global `LiON = LiONStandard()` and loads `@scripts/init.lion` before the loop. `start(mode="lion")`:

1. Executes initialization with `LiON.parsefunc(init)`.
2. Chooses `ImpossibleError` when the `throw_err` node is true, otherwise catches broad `Exception`.
3. Reads `LiON.stdin()` using a prompt containing throw/security/debug indicators and DMS cwd.
4. Accumulates lines until `count_brackets()` reports balanced `()`, `[]`, `{}` outside double-quoted strings.
5. Handles `!exit` and `!mode <name>` special commands.
6. In `lion` mode, calls `parsefunc`; non-`None` results are passed to `format_out()` unless debug is active.
7. In `cmd` mode, passes the raw input to `os.system`.
8. Prints exceptions; in debug mode also prints a traceback; resets the input buffer in `finally`.

The basic shell has no line-editing or persistent history and does not explicitly catch `KeyboardInterrupt`/`EOFError` separately.

### 3.3 Enhanced LSI shell

[`LiON_shell/LSI`](./LiON_shell/__init__.py) subclasses `LiONStandard` and adds:

- `PromptSession`, `InMemoryHistory`, `AutoSuggestFromHistory`, `WordCompleter`.
- Pygments syntax highlighting through [`LiON_shell/lexman.py`](./LiON_shell/lexman.py).
- True-color styles, bottom toolbar, cwd/security/debug/error indicators.
- `shellinit.lion` execution by default.
- `!exit` handling and a module-level `mode` variable (`lion`/`cmd`).
- `prompt()` multiline accumulation until bracket balance; `KeyboardInterrupt` returns from the prompt.

`run()` refreshes completion words from root keys each iteration, switches toolbar visibility based on the `shell` config node, parses LiON input, or invokes `os.system` in command mode. It catches `KeyboardInterrupt`, `EOFError`, and configured runtime exceptions. The final `except not self[...] and exptype` clause is syntactically questionable and should be treated as a migration compatibility issue rather than relied upon.

`format_out()` prints `[type] out:` and JSON-formats dictionaries. `typeof()` classifies primitive Python values, call-code lists, and node dictionaries.

### 3.4 Lexer and source grammar

[`full_lexer()`](./LiON/lexer.py) is the pipeline:

```text
source
  -> lexer_delimiter
  -> lexer_tokenizer per call
  -> lexer_categorize
  -> lexer_condemner for each token
  -> list[call-dict]
```

#### Delimiting and comments

- Top-level calls are separated by newline or `;` (`CALLS_DELIMITERS`).
- A newline after `;` is suppressed as a second delimiter.
- `#` starts an inline comment outside strings.
- `/* ... */` is a multiline comment; `remove_comments()` also exists but `lexer_delimiter()` performs its own stateful handling.
- Brackets `{}`, `[]`, `()` suppress call/token delimiters while open.
- Double quotes toggle string state; escaped quote handling is limited because the state machine toggles on every `"`.
- Mismatched brackets raise `BracketMismatch`; unclosed brackets raise `BracketNeverClosed`; unclosed strings raise `StringNeverClosed`.

#### Token forms

`lexer_condemner()` recognizes:

- `&(...)` list literals.
- `{...}` code blocks recursively lexed to call dictionaries.
- `[...]` masks, recursively parsed as a call.
- `...[...]` distribution masks.
- `?value` literal masks.
- `(a,b)` tuples and `(key:value,...)` dictionaries.
- `(...)=>{...}` lambda expressions, rewritten to `new lam (...) {...}`.
- `pathname[...]` function masks.
- `"..."` escaped strings, `r"..."` raw strings, and `d"..."` DMS directory strings.
- integers, decimals, `f` floats, and `%` percentages.
- `on/off/true/false` booleans and `none/null/nil` null.
- `::path` pathname getter rewrite to a `get` call.
- unrecognized tokens as `STRING_UNKNOWN`.

`lexer_key_value()` tracks nested brackets and strings, uses `:` and `,`, and drops empty keys. `lexer_parenthesis()` chooses dictionary vs tuple based on a top-level colon. Collections use comma splitting outside nested brackets/strings.

#### Call dictionary schema

`build_call()` creates dictionaries with:

- `pathname`: target node/path or synthetic `return`.
- `kw`: restriction keywords (`only`, `final`, `protect`, `cascade`, `static`) when present.
- `posargs`: condemned positional tokens.
- `implicit`: `->` key/value arguments.
- `inserting`: `<-` key/value arguments (captured by lexer but not consumed in the shown parser path).
- `scope`: `global`, `local`, or `nonlocal`.

Keywords must precede the pathname. The pathname itself may be a mask; if it is not an unknown string, the lexer turns it into an expression argument and uses `return`. `break` and `continue` remain pathnames and are intercepted by `parse_calls_direct()`.

### 3.5 Parser, evaluator, and execution engine

The parser is an interpreter over node dictionaries. `TreeManager.parsefunc()` lexes source then calls `parse_calls_direct()`. There is no independent AST class hierarchy.

#### Core execution dispatch

`TreeManager.exec(node, args, kwargs, restrictions, constructor, scope)` dispatches on `node["__class__"]`:

- `builtin`/`statement`: call the Python callable in `__rel__`, passing restrictions/scope metadata.
- constructor-like classes: call `new()`, optionally return the built node or pack it into the selected scope.
- `version`: produce a formatted version string.
- variable-like classes: index/iterate the relative value through `exec_variable_like`.
- `saber`: execute code in a scope with argument metadata.
- function/lambda: bind arguments, push a scope, and parse function code.
- overload: select an overload by argument count, with `_` as fallback.
- method: resolve the receiver pathname, then class method `%<name>`.
- alias: recursively call the pointed pathname.
- exception: raise `NodeThrownError`.
- other classes: call the class `exec` method.

`call()` resolves a pathname, executes it, and deletes it afterward when it has `only`. `scoped_exec()` adds a temporary scope and optional references. The `@scoped` decorator guarantees release in `finally`, but can still mask an earlier error if release itself fails.

#### Parse loop

`parse_call()` resolves token values, expands masks/lists/tuples/dictionaries, and calls the target. `parse_calls_direct()` executes sequentially, stores each non-`None` result in root `out`, and stops on `AbstractInternal` control values. `parse_calls()` wraps a list in a temporary scope. `parsefunc()` is the source boundary.

#### Control flow

`LiONBasic` implements:

- `if`/`elif`/`else` via `lexer_cascade`, with optional `cascade` restriction.
- `switch`/`case`/`default`.
- `do`, `while`, `repeat`, `each`, tuple/string iterators, `filter`, and `for`.
- `break`/`continue` as `AbstractInternal` values.
- `try`/`catch`/`finally`, mapping Python exceptions to exception nodes.
- `return` through expression/mask handling and internal call results.

Loop variables are packed as tree nodes and mutated with `set_rel`; loop bodies execute in temporary scopes but commonly write variables into the current tree head.

#### Operators

`OperatorManager.shunting_yard()` converts nested expression lists to postfix using registry precedence. `parse_sorted()` evaluates postfix using unary/binary operator types. Standard operators are node dictionaries in `STANDARD_OPERATORS`; default operators call Python lambdas directly, while user operators call `TreeManager.exec_function()`.

### 3.6 Node data model, scope, and environment

#### Node structure

The minimum node shape is:

```python
{
    "__name__": str,
    "__class__": str,
    "__rel__": Any,
    "__rs__": tuple[str, ...],        # optional restrictions
    "__doc__": str, "__tag__": Any,   # optional metadata
}
```

Function nodes add `__args__` and one parameter node per argument. Classes contain method nodes named with `%` plus method names. Constructors may add `__for__`; instances may add `__instanceof__`. Operators add `type`, `proc`, and `lam`. Locale nodes add semantic and alias maps.

`is_node()` means “dictionary containing `__class__`”, so arbitrary dictionaries can become node-like if they contain that key. `is_code()` means a non-empty list where every item is a dictionary containing `pathname`.

#### Root tree and registries

`construct_tree()` creates a root `newable` node containing:

- `reg`: registry domains `op`, `classes`, `task`, `locale`, `perm`, `except`, `dms`.
- `out`, `debug`, and `throw_err` tree configuration nodes.

`LiONBasic.setup()` populates these and applies `protect` recursively. Registry promotion uses `REGISTRY_CLASS_BINDING`; classes, exceptions, locales, DMS values, tasks, and operators are promoted by class.

#### Scope stack

`Scope.scope_stack` is a list of dictionaries. Index `0` is the global root; the last entry is the current head. `get()` searches from head to root unless a `global`/`local` scope is specified. `add_scope()` constructs a scope node/dictionary, and `release()` pops it; releasing the global scope raises `SystemError`.

Function execution mutates parameter node relatives before pushing a function scope. The scope receives `__name__`, `this`, argument parameter nodes, and explicit references such as `self`. This is a dynamically scoped, mutable environment rather than an immutable lexical closure model.

#### Restrictions and mutation

`protect` prevents `pop`; `final` prevents changing a node’s relative; `only` makes a called node one-shot; `cascade` changes conditional behavior; `static` is a declaration marker. `pack_exact()` enforces class compatibility on override. `conf_exact()` permits broad attribute mutation except protected/final cases. Assertions are used in many structural guards.

### 3.7 Built-ins, standard library, and native integrations

`LiONBasic.get_basic()` registers tree management (`get`, `pack`, `drop`, `move`, `rename`, `new`, `call`, `exec`, `conf`, `set`, `mut`, `promote`, `demote`), control flow, constructors (`node`, `struct`, `class`, `function`, `lam`, `operator`, etc.), collection/math builtins, I/O, and type checks.

`LiONStandard.get_standard()` adds reset/repair, lexer and JSON lexer output, tree visualization, printing, math, time, input, shell, and cast modules. Python standard modules are exposed through `LiON/std/*.py`, often using module-level `parent_parser` globals injected by `execute_python()`.

Native/system edges include:

- `execute_python()` compiles and executes arbitrary Python source.
- `lsh.py` calls `os.system` and `subprocess.Popen`; process handles are wrapped into nodes.
- DMS calls `os.chdir`, reads files, and exposes cwd/home.
- `timeout` starts `threading.Timer`; `timeit` executes parser code repeatedly.
- `neo/style.py` parses YAML with `yaml.FullLoader`.
- prompt-toolkit/Pygments provide the enhanced terminal UI.

## 4. State & Memory Model

### 4.1 Values and ownership in Python

All runtime values are ordinary Python objects held by references in dictionaries, lists, tuples, closures, and node relatives. There is no custom allocator or garbage collector. Python reference counting plus cyclic garbage collection owns lifetime. The root graph can retain objects indefinitely through registries, aliases, closures, and Python callable references.

### 4.2 Call frames and closures

A call frame is an appended dictionary in `scope_stack`. Function parameters are stored as mutable parameter nodes inside the function node and have their `__rel__` overwritten at invocation. `exec_function()` then adds `this`, `__name__`, and parameter references to the head. This creates observable mutation and makes concurrent invocation of the same function node unsafe.

Closures are not represented by an explicit captured environment object. Nested functions can observe the current stack/tree through path lookup and references; the effective behavior is a mixture of dynamic scope, shared mutable root state, and retained Python objects.

### 4.3 REPL lifecycle

1. Construct one `LiONStandard`/`LSI`.
2. Build and protect the root tree.
3. Run init scripts.
4. For every input, lex and execute against the same root and current global registries.
5. Temporary scopes are released after a call/control-flow body.
6. User-created nodes, imported modules, cwd changes, aliases, locale aliases, and mutations survive until reset or process exit.

`LiONStandard.reset()` clears the root and restores a shallow copy of `backup_root`, then reruns setup. The shallow copy means nested object identity and external references require careful compatibility testing.

### 4.4 File/CLI lifecycle

`-r` uses one runtime for one source file and exits. `-c` creates no evaluation frame; it emits lexed call dictionaries wrapped in a variable node. `-exec` creates a fresh `LiONStandard`, loads the JSON node, dispatches it, formats output, and exits. A compiled JSON file therefore preserves token/call representation, not a fully resolved executable closure or serialized Python callable.

## 5. Migration & Rust Translation Footprint

### 5.1 Suggested Rust mapping

| Python abstraction | Rust direction |
|---|---|
| Node dictionaries with dynamic `__class__` | `enum NodeKind` plus `struct Node { name, kind, relative, metadata }`; use a typed `Value` enum for relative values. |
| Arbitrary runtime values | `enum Value { Null, Bool, Int, Float, String, List, Tuple, Map, Node, Code, Builtin, ... }`; decide explicitly which values are serializable. |
| Root `dict` tree and pathnames | `Tree`/`Environment` with `IndexMap<String, Value>` or `HashMap`; preserve insertion ordering if UI/tests depend on it. |
| `scope_stack: list[dict]` | `Vec<ScopeFrame>` with explicit lookup policy (`Global`, `Local`, `Nonlocal`, `Default`). |
| Python callables in `__rel__` | `enum Callable` for native builtins and user functions; trait object only where dynamic extension is required. |
| Function mutation of parameter nodes | Per-call `Frame` bindings; do not mutate function definitions. This is a deliberate semantic hardening and must be compatibility-tested. |
| Decorator `@scoped` | RAII guard whose `Drop` releases a frame, plus explicit error propagation. |
| Recursive lexer/parser | Iterative scanners where practical; return `Result<T, LexError>`/`ParseError` with spans. |
| Condemned `(type, value)` tuples | Typed `TokenValue` enum and source span. |
| Call dictionaries | `Call { path, restrictions, positional, implicit, inserting, scope }`. |
| `AbstractInternal` | `ControlFlow::{Break, Continue, Return(Value)}`; use `Result<ControlFlow<Value>, RuntimeError>`. |
| Operator lambdas and precedence | `OperatorSpec { fixity, precedence, implementation }`; shunting-yard or Pratt parser with typed operands. |
| `copy.deepcopy` | Explicit clone policies; use `Arc` only for intentional shared immutable data. |
| Aliases | `Path` reference with cycle detection and a defined mutation policy. |
| Python exceptions | Typed `enum RuntimeError` with source span, node path, and optional LiON exception payload. |
| JSON compiled format | Versioned serde schema; reject unsupported versions and distinguish serialized values from executable native functions. |
| Python `threading.Timer`/subprocess | Tokio or standard threads/process APIs behind capability interfaces. |
| YAML/JSON/assets | `serde_json`, `serde_yaml`, embedded/resource loaders with deterministic path resolution. |
| Pygments/prompt_toolkit | Rust shell abstraction; preserve a headless REPL core separately from terminal UI. |

### 5.2 Recommended Rust architectural boundaries

1. **`syntax`**: source spans, comments, scanner, token values, grammar, diagnostics.
2. **`ir`**: versioned call representation; JSON compatibility layer.
3. **`value`**: runtime values, nodes, callable references, serialization rules.
4. **`environment`**: tree, registries, scope frames, path resolution, restrictions.
5. **`eval`**: dispatch, argument binding, control flow, operators, errors.
6. **`stdlib`**: pure functions first; filesystem/process/time as capability-injected services.
7. **`cli`**: typed command parsing, exit-code policy, file compilation/execution.
8. **`shell`**: reusable input/evaluation/output service with terminal adapters.

Keep a Python-compatible JSON reader/writer at the boundary during incremental migration. A Rust evaluator can initially consume the existing call dictionaries while Python extensions remain behind a bridge, but native Python function references cannot be faithfully serialized.

### 5.3 Bottlenecks and migration risks

- **Dynamic node classes:** `exec()` depends on string class names and fallback method dispatch. A Rust enum must preserve unknown/custom classes or provide an explicit extension registry.
- **Mutable function definitions:** parameter relatives are overwritten on invocation, causing reentrancy and concurrency hazards. Rust should isolate call bindings while offering a compatibility mode if observable.
- **Dynamic path lookup:** aliases, `global`/`local` lookup, dot paths, and runtime-created names make static analysis difficult. Add path resolution tests and cycle detection.
- **Python import injection:** `execute_python()` is an embedded scripting ABI, not merely a library import. Full migration requires a replacement extension ABI or a deliberately frozen Python bridge.
- **Callable identity:** builtins and lambdas live inside Python objects and are not represented in compiled JSON. Define native IDs and registration/versioning.
- **Exception inconsistency:** LiON exceptions coexist with assertions and native errors. Rust must first inventory which error text/types are user-visible, then normalize without silently changing contracts.
- **Lexer edge cases:** bracket/string state is hand-written; escaped quotes, malformed nesting, empty masks, comments, and dictionary delimiters are compatibility-sensitive.
- **Unimplemented/partially wired fields:** `inserting` is lexed but not consumed in the visible parse path; `static` and `nonlocal` are accepted as syntax but have limited explicit behavior; `cache` is a placeholder.
- **Security boundary:** `os.system`, subprocesses, filesystem mutation, Python `exec`, and unrestricted imports mean the current interpreter is not sandboxed. Rust capability APIs must make this choice explicit.
- **Concurrency:** `threading.Timer`, subprocess nodes, mutable global root state, and function parameter mutation are not thread-safe. The GIL currently serializes some Python bytecode but does not make semantic state safe.
- **Resource resolution:** DMS symbols depend on module location, cwd, and home. Rust packaging must define deterministic asset lookup independent of the launch directory.
- **Ordering and identity:** dictionary insertion order, object identity (`is`), shallow backup copies, and alias references may be observable.
- **Third-party shell behavior:** prompt-toolkit and Pygments provide terminal features that should not be coupled to evaluator correctness.
- **YAML loading:** `yaml.FullLoader` is an input and compatibility concern; Rust should use a constrained schema and safe loader.
- **Path portability:** source uses mixed slash construction and `sys.path` manipulation; Windows and POSIX behavior must be tested separately.

### 5.4 Migration invariants to preserve

- Exact call-dictionary fields and JSON round-trip behavior for supported compiled files.
- Source ordering and semicolon/newline behavior.
- Quoted-string, mask, tuple/list/dictionary, percentage, pathname, and lambda semantics.
- Root tree names, registry domains, node attributes, restrictions, aliases, and method naming (`%method`).
- Scope lookup precedence and explicit scope keywords.
- `out` updates and shell output formatting where user-visible.
- Operator precedence and unary/binary evaluation.
- Exception class/message mapping where scripts catch or display them.
- DMS symbol meanings and resource paths.
- `only`, `final`, `protect`, and `cascade` effects.
- Distinct one-shot CLI exit behavior (`0` success, `2` validation/input errors), while deciding how runtime errors should map.

## 6. End-to-End Control-Flow References

### Source execution

```text
CLI -r
  -> _path_argument
  -> LiONStandard.run_statement
  -> funclib.loadRaw / DMS.parse
  -> TreeManager.parsefunc
  -> full_lexer
  -> parse_calls_direct
  -> parse_call
  -> Scope.get / TreeManager.call
  -> TreeManager.exec
  -> builtin/function/constructor/method/operator
  -> root/out and stdout
```

### Compilation and execution

```text
CLI -c
  -> read UTF-8 source
  -> full_lexer
  -> construct_variable(input_name, call_list)
  -> json.dumps
  -> temporary file + os.replace

CLI -exec
  -> read UTF-8 JSON
  -> json.loads
  -> LiONStandard.exec(node)
  -> dispatch serialized node
  -> format_out + print_finished
```

### Shell input

```text
prompt_toolkit/basic input
  -> bracket balance accumulator
  -> special shell command or LiON source
  -> parser/evaluator
  -> format_out / print_exception
  -> persistent root for next prompt
```

This document is intentionally the single prose baseline requested for the repository. It describes current behavior, including quirks and incomplete seams, rather than prescribing an already-committed Rust design.
