<p align="center">
  <img src="img/icon.png" alt="Luz logo" width="120">
</p>

# Luz Programming Language

**Luz** is a lightweight, interpreted programming language written in Python. It is designed to be simple, readable, and easy to learn.

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

## Why Luz?

- **No boilerplate** — variables need no declaration keyword, blocks use `{ }`
- **Readable syntax** — keywords read like English (`for i = 1 to 10`, `attempt / rescue`)
- **Full OOP** — classes, inheritance, method overriding, `super`
- **First-class functions** — lambdas, closures, higher-order functions
- **Helpful errors** — every error includes the source line number
- **Zero dependencies** — just Python 3.8+

## Quick Example

```
class Animal {
    function init(self, name) {
        self.name = name
    }
    function speak(self) {
        write($"{self.name} says hello!")
    }
}

class Dog extends Animal {
    function speak(self) {
        super.speak()
        write("(woof!)")
    }
}

d = Dog("Rex")
d.speak()
```

## Features at a glance

| Feature | Syntax |
|---|---|
| Variable | `x = 10` |
| Format string | `$"Hello {name}"` |
| For range | `for i = 1 to 10 { }` |
| For each | `for item in list { }` |
| Lambda | `fn(x) => x * 2` |
| Class | `class Dog extends Animal { }` |
| Error handling | `attempt { } rescue (e) { }` |
| Import | `import "utils.luz"` |

## Get Started

Head to [Installation](getting-started/installation.md) to set up Luz, or jump straight into the [Language Reference](language/types.md).
