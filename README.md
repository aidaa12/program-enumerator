# Week 4 – Program Enumerator

Bottom-up enumerative synthesizer for `E ::= x | y | 0 | 1 | 2 | + E E | - E E | * E E`.

    python3 synth.py examples.txt     # prints the smallest matching program, or "No program found"
    python3 synth.py --test tests     # runs every test in tests/

## How it works

1. **Size = number of tokens.** Programs of size 1 are the terminals; a program of size n is
   an operator plus a left subprogram of size l and a right one of size n-1-l.
   We build size 1, 2, 3, ... in order, so the first match is a smallest program.
2. **Value vectors.** Each program is stored with its outputs on all examples, so combining
   two programs is just an elementwise `+`, `-`, or `*` on their vectors (no re-evaluation).
3. **Observational-equivalence pruning.** If a new program's value vector was already produced
   by a smaller/earlier program, it is thrown away. Safe because the DSL is pure arithmetic
   (a subterm's meaning does not depend on its context).
4. **Termination.** Stops at `max_size` (default 11) and reports failure (used for the `max(x, y)` test).

Tie-breaking (same size): terminals in order x y 0 1 2, operators in order + - \*, smaller left subtree first.
This reproduces every program in the answer key.
