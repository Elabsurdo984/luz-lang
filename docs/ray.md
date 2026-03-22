# Ray Package Manager

Ray is the official package manager for Luz. It installs packages from GitHub directly into your project.

## Commands

```bash
ray init                   # create a luz.json in the current directory
ray install user/repo      # install a package from GitHub
ray list                   # list installed packages
ray remove package-name    # remove a package
```

## Installing a package

```bash
ray install Elabsurdo984/luz-utils
```

Ray downloads the repository as a zip, extracts it, and places it in `luz_modules/<name>/`. After installing, import it normally:

```
import "utils"
```

## Creating a library

Any Luz project can be published as a package. The only requirement is a `luz.json` file at the root.

**luz.json**
```json
{
  "name": "my-library",
  "version": "1.0.0",
  "description": "My Luz library",
  "author": "yourname",
  "main": "my-library.luz"
}
```

- `name` — the name users will use to import your library.
- `main` — the entry point file that gets executed on `import "my-library"`.

**Recommended structure**

```
my-library/
├── luz.json
├── my-library.luz       ← entry point (imports the modules below)
├── core.luz
├── utils.luz
└── helpers.luz
```

**my-library.luz**
```
import "core.luz"
import "utils.luz"
import "helpers.luz"
```

Users install it with:

```bash
ray install yourname/my-library
```

And use it with:

```
import "my-library"
```

## Project manifest

`ray init` creates a `luz.json` for your project:

```json
{
  "name": "my-project",
  "version": "0.1.0",
  "description": "",
  "author": ""
}
```

## luz_modules/

Installed packages live in `luz_modules/` inside your project. Add this folder to `.gitignore` if you don't want to commit dependencies.

```
luz_modules/
├── my-library/
│   ├── luz.json
│   └── my-library.luz
```
