# Operators in LiON
This section is to explain how operators are used in LiON, it's functionality and usages.

## The builtin `$`
To use operators, you must use the `$` builtin as for evaluating given expressions.
All numbers and operands must be separated by spaces. See down an example:
```lion
# Do some simple arithmetic
set basic [$ 7 + 1 * 9 - 3]
echo ?basic
```
### Rounding
The `$` builtin supports an implicit argument specific to round a number to n decimal places, see below

```lion
# Round an expression's result to only 2 decimal places.
$ 0.2 + 0.1 -> (r: 2)
```

## The modulus operator %
This operator returns the rest of integer division, or it can be used to format strings, see down below:
```lion
# Convert seconds to hours, minutes and seconds
set given   [cast.int [input "Type some seconds: "]]
# Processing
set seconds [$ ?given // 3600]
set minutes [$ [$ ?given % 3600] // 60]
set hours   [$ [$ ?given % 3600] // 60]

# Using the `%d` mark for integers
echo [$ "Hours %d"   % ?hours]
echo [$ "Minutes %d" % ?minutes]
echo [$ "Seconds %d" % ?seconds] 
```

---

## LiON's full operators table
Here it is a full list of all LiON's operators, names, and functionality

| **Operator** | **Name**            | **Description**                                                         |
|--------------|---------------------|-------------------------------------------------------------------------|
| +            | Plus                | Adds two numbers, concatenate strings and iterables                     |
| -            | Minus               | Subtracts two numbers                                                   |
| * of         | Multiplication      | Multiplies two numbers, extends a string or iterable                    |
| / :          | Division            | Divides two numbers, returns a float                                    |
| //           | Integer Division    | Does integer division, returns an integer as opposed to /               |
| %            | Modulus             | Rest of division, string formatting                                     |
| **           | Exponentiation      | Returns the power of a base elevated to a given exponent                |
| @            | Square root         | Returns the square root of a number                                     |
| <= < > >=    | Inequality          | Compares two numbers, > greater < smaller                               |
| == !=        | Equality            | Checks if two numbers are equal or not equal                            |
| not          | Logical NOT         | Logical NOT, negates a given boolean                                    |
| and          | Logical AND         | Logical AND, if both booleans are true, return true                     |
| or xor       | Logical OR and XOR  | Logical inclusive and exclusive OR                                      |
| U !U         | Union, Intersection | Set union and intersection                                              |
| in           | Membership operator | Check if the given thing is member of an iterable                       |
| C            | Subset operator     | Check if a given iterable is a subset of another                        |
| oc           | Count operator      | Counts how many occurrences of a thing in an iterable                   |
| ~            | Inclusive range     | Incluive range, returns numbers from A to B                             |
| ~~           | Exclusive range     | Exclusive range, returns numbers between A and B, not including A and B |
| scale        | Scaling operator    | Scale operator, converts a number up into a given decimal scale         |
| downscale    | Downscaling operato | Converts a number down into a given decimal scale                       |

# Operator type table:

| **Operator** | **Type** | **Returns**               | **Priority** |
|--------------|----------|---------------------------|--------------|
| +            | Binary   | Number, string, iterables | 6            |
| -            | Binary   | Number                    | 6            |
| * of         | Binary   | Number, string, iterables | 7            |
| / :          | Binary   | Number                    | 7            |
| //           | Binary   | Number                    | 7            |
| %            | Binary   | Number                    | 7            |
| **           | Binary   | Number                    | 8            |
| @            | Unary    | Number                    | 8            |
| <= < > >=    | Binary   | Boolean                   | 4            |
| == !=        | Binary   | Boolean                   | 4            |
| not          | Unary    | Boolean                   | 3            |
| and          | Binary   | Boolean                   | 2            |
| or xor       | Binary   | Boolean                   | 1            |
| U !U         | Binary   | Iterable                  | 5            |
| in           | Binary   | Boolean                   | 4            |
| C            | Binary   | Boolean                   | 5            |
| oc           | Binary   | Number                    | 5            |
| ~            | Binary   | Iterable                  | 7            |
| ~~           | Binary   | Iterable                  | 7            |
| scale        | Binary   | Number                    | 5            |
| downscale    | Binary   | Number                    | 5            |