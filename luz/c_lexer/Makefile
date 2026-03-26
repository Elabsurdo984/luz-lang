CFLAGS = -Wall -Wextra -O2

ifeq ($(OS), Windows_NT)
	# MSYS2 MinGW-w64 produces a 64-bit DLL that matches Python's architecture.
	# We invoke it through MSYS2's bash so that TMP is set correctly (the bare
	# gcc.exe call fails when TMP is unset and it cannot find a temp directory).
	LIB   = luz_lexer.dll
	BUILD = C:/msys64/usr/bin/bash.exe -l -c \
	          'export TMP=/tmp TEMP=/tmp TMPDIR=/tmp && \
	           gcc -Wall -Wextra -O2 -shared luz_lexer.c -o luz_lexer.dll'
	BUILD_TEST = C:/msys64/usr/bin/bash.exe -l -c \
	               'export TMP=/tmp TEMP=/tmp TMPDIR=/tmp && \
	                gcc -Wall -Wextra -O2 -DLUZ_TEST luz_lexer.c -o lexer_test && \
	                ./lexer_test'
else
	LIB        = luz_lexer.so
	BUILD      = gcc $(CFLAGS) -shared -fPIC luz_lexer.c -o $(LIB)
	BUILD_TEST = gcc $(CFLAGS) -DLUZ_TEST luz_lexer.c -o lexer_test && ./lexer_test
endif

# Default target: shared library
$(LIB): luz_lexer.c luz_lexer.h
	$(BUILD)
	@echo "Built $(LIB)"

test: luz_lexer.c luz_lexer.h
	$(BUILD_TEST)

clean:
	rm -f $(LIB) lexer_test lexer_test.exe

.PHONY: test clean