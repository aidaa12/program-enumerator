#!/usr/bin/env python3
"""Bottom-up enumerative program synthesizer for the arithmetic DSL

    E ::= x | y | 0 | 1 | 2 | + E E | - E E | * E E

Programs are written in Polish (prefix) notation
Programs are enumerated in order of increasing size (number of tokens) and the
first one that matches every input/output example is returned.

Usage:  python3 synth.py examples.txt      (each line: "i1, i2, o1")
        python3 synth.py --test DIR [KEY]   (run every *.txt in DIR)
"""
import sys, os, time

TERMINALS = ["x", "y", "0", "1", "2"]
OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
}


def parse_examples(text):
    """Parse lines of the form 'i1, i2, o1' into [(i1, i2, o1), ...]."""
    ex = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        a, b, o = (int(t) for t in line.split(","))
        ex.append((a, b, o))
    return ex


def terminal_values(tok, examples):
    """The 'value vector' of a terminal: its output on every example input."""
    if tok == "x":
        return tuple(a for a, _, _ in examples)
    if tok == "y":
        return tuple(b for _, b, _ in examples)
    return tuple(int(tok) for _ in examples)


def synthesize(examples, max_size=11):
    """Return (program_string, num_programs_kept) or (None, num_programs_kept).

    Bottom-up enumeration. by_size[n] stores kept programs of size n.
    Programs with the same value vector are pruned as equivalent.
    """
    target = tuple(o for _, _, o in examples)
    seen = set()          # value vectors already produced by some smaller/earlier program
    by_size = {}          # size -> list of (program string, value vector)
    kept = 0

    # Size 1: terminals
    level = []
    for tok in TERMINALS:
        vals = terminal_values(tok, examples)
        if vals in seen:
            continue
        seen.add(vals)
        level.append((tok, vals))
        kept += 1
        if vals == target:
            return tok, kept
    by_size[1] = level

    # Size n >= 3: an operator (1 token) + left subterm (size l) + right subterm (size n-1-l)
    # Binary ops only, so sizes are always odd; even sizes are empty.
    for n in range(2, max_size + 1):
        level = []
        for op, fn in OPS.items():
            for l in range(1, n - 1):
                r = n - 1 - l
                lefts, rights = by_size.get(l, []), by_size.get(r, [])
                if not lefts or not rights:
                    continue
                for lp, lv in lefts:
                    for rp, rv in rights:
                        vals = tuple(fn(a, b) for a, b in zip(lv, rv))
                        if vals in seen:
                            continue          # observationally equivalent to something we have
                        seen.add(vals)
                        prog = f"{op} {lp} {rp}"
                        level.append((prog, vals))
                        kept += 1
                        if vals == target:
                            return prog, kept
        by_size[n] = level
    return None, kept


def evaluate(prog, x, y):
    """Evaluate a prefix program (used only for sanity checking)."""
    toks = prog.split()
    pos = 0

    def go():
        nonlocal pos
        t = toks[pos]
        pos += 1
        if t == "x": return x
        if t == "y": return y
        if t in OPS:
            a = go()
            b = go()
            return OPS[t](a, b)
        return int(t)
    return go()


def run_file(path, max_size=11):
    with open(path) as f:
        ex = parse_examples(f.read())
    t0 = time.time()
    prog, n = synthesize(ex, max_size)
    return prog, n, time.time() - t0, ex


def main(argv):
    if len(argv) >= 2 and argv[0] == "--test":
        d = argv[1]
        for name in sorted(os.listdir(d)):
            if not name.endswith(".txt"):
                continue
            prog, n, dt, ex = run_file(os.path.join(d, name))
            ok = prog is None or all(evaluate(prog, a, b) == o for a, b, o in ex)
            print(f"{name[:-4]:24s} {str(prog):28s} ({n} programs, {dt:.2f}s) {'OK' if ok else 'WRONG'}")
        return
    if len(argv) != 1:
        print(__doc__)
        sys.exit(1)
    prog, n, dt, _ = run_file(argv[0])
    print(prog if prog is not None else "No program found")


if __name__ == "__main__":
    main(sys.argv[1:])
