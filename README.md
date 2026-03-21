<p align="center">
  <img src="img/icon.png" alt="Luz logo" width="120">
</p>

# Luz Programming Language

**Luz** is a lightweight, interpreted programming language written in Python. Designed to be simple, readable, and easy to learn.

```
name = listen("What is your name? ")
write($"Hello {name}!")

for i = 1 to 5 {
    if even(i) {
        write($"{i} is even")
    } else {
        write($"{i} is odd")
    }
}
```

## Features

- **Dynamic typing** — integers, floats, strings, booleans, lists, dictionaries, `null`
- **Format strings** — `$"Hello {name}, you are {age} years old!"`
- **Control flow** — `if / elif / else`, `while`, `for` (range and for-each), `break`, `continue`, `pass`
- **Functions** — user-defined functions with closures and return values
- **Lambdas** — `fn(x) => x * 2` and `fn(x) { body }` as first-class values
- **Object-oriented programming** — classes, inheritance (`extends`), method overriding, `super`
- **Polymorphism** — duck typing, `typeof()`, and `instanceof()`
- **Error handling** — `attempt / rescue` blocks and `alert`
- **Modules** — `import` other `.luz` files
- **Math built-ins** — `abs`, `sqrt`, `floor`, `ceil`, `round`, `clamp`, `max`, `min`, `sign`, `odd`, `even`
- **Helpful errors** — every error includes the line number
- **REPL** — interactive shell for quick experimentation
- **VS Code extension** — syntax highlighting included

## Quick start

Requires **Python 3.8+**, no external dependencies.

```bash
git clone https://github.com/Elabsurdo984/luz-lang.git
cd luz-lang
python main.py          # open the REPL
python main.py file.luz # run a file
```

## Documentation

Full language reference, built-in functions, and architecture guide:
**[elabsurdo984.github.io/luz-lang](https://elabsurdo984.github.io/luz-lang/)**

## License

MIT — see [LICENSE](LICENSE) for details.
