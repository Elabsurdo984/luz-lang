# luz-io

File I/O utilities included with Luz. No installation needed.

```
import "io"
```

---

## Files

### `copy_file(src, dst)`
Copies the contents of `src` into `dst`.

```
copy_file("input.txt", "backup.txt")
```

### `read_file_or(path, default_value)`
Reads a file and returns its content. Returns `default_value` if the file does not exist.

```
content = read_file_or("config.txt", "")
```

### `write_file_new(path, content)`
Writes `content` to a file only if the file does not already exist. Raises an error if the file is already there.

```
write_file_new("output.txt", "hello")
```

---

## Lines

### `read_lines(path)`
Reads a file and returns its lines as a list of strings. Newlines are stripped.

```
lines = read_lines("data.txt")
for line in lines {
    write(line)
}
```

### `write_lines(path, lines)`
Writes a list of strings to a file, one per line.

```
write_lines("out.txt", ["line1", "line2", "line3"])
```

### `append_line(path, line)`
Appends a single line to a file.

```
append_line("log.txt", "new entry")
```

### `count_lines(path)`
Returns the number of lines in a file.

```
write(count_lines("data.txt"))   # 42
```

### `read_line(path, n)`
Returns the nth line of a file (0-indexed). Raises an error if `n` is out of range.

```
first = read_line("data.txt", 0)
```

---

## CSV

### `read_csv(path)`
Reads a CSV file and returns a list of rows. Each row is a list of strings. The first row is the header.

```
rows = read_csv("data.csv")
for row in rows {
    write(row[0])
}
```

### `read_csv_dict(path)`
Reads a CSV file as a list of dictionaries, using the first row as keys.

```
records = read_csv_dict("people.csv")
for record in records {
    write(record["name"])
}
```

### `write_csv(path, rows)`
Writes a list of rows (list of lists) to a CSV file.

```
data = [["name", "age"], ["Alice", "30"], ["Bob", "25"]]
write_csv("output.csv", data)
```
