# The lionc.py CLI tool 🦁
This tool allows for you to run LiON scripts from outside the LSI, while also, 
permitting you to use it for compiling and running scripts and labels.

## Install and configuration
Get the tool, then put the lionc.py script right on the root of the repository.
> Depending on your OS, it is a good idea to put the tool inside your PATH.

## Usage
The basic syntax for lionc.py is:
```bash
python3 lionc.py <mode> <args>
```
The modes are actually which operations do you want the tool to execute, currently, there are:
* `-h`: Help, prints this file into the terminal screen
* `-sh`: Starts the simple shell
* `-i`: Starts the LSI, with the `init.lion` script
* `-wi`: Opens LSI, without using the init.lion script
* `-r`: Runs a given `.lion` script from a filepath:
  * `... -r <filepath>`
* `-c`: Compiles a given script into an executable label.
  * `... -c <input_filepath> <output_filepath>`
* `-exec`: Executes a given label.
  * `... -exec <input_filepath>`

# Author and Copyright
Felipe Fernandes ([rkhue](https://www.github.com/rkhue/) at GitHub)