# Design decisions and tradeoffs

## 1. Functional public operations

**Decision:** Use `resize()` for ordinary transformations and `plan()` when one
set of seam decisions must produce both a result and a preview.

The earlier mutable `SeamCarver` class was retained while these operations were
introduced, then removed during beta. It did not cache energy maps or seam
decisions, so it offered no computational advantage over the functional API.

Benefits:

- Source inputs are not mutated.
- A failed operation cannot leave a public object partially updated.
- Explicit input and output values are easier to test, retry, and pass to a
  background worker.

Tradeoff:

- Callers performing several transformations must reassign each result.

## 2. One stateful result type

**Decision:** Keep `ResizePlan` as the only stateful public image-operation
object.

A plan stores the source, carved result, and source-coordinate removal mask.
This avoids repeating seam search when a caller needs both `carve()` and
`highlight()`. Stored arrays are read-only, and each output method returns an
owned copy.

Tradeoff:

- A plan retains several arrays until it is released.

## 3. Compatible energy callables

**Decision:** Accept plain functions and callable objects while retaining
`EnergyMethod` for existing class-based implementations.

`SeamCalculator` validates every returned energy map before search. The map must
be a finite, real, two-dimensional numeric array matching the current image.

Tradeoff:

- Validation and normalization add one full-map pass.

The CLI exposes only built-in methods. A CLI plugin system remains deferred
until there is a demonstrated use case.

## 4. Vertical search with transposed height processing

**Decision:** Implement one vertical seam-search algorithm. Height reduction
transposes the current image and source-coordinate map before using the same
logic.

This avoids duplicate dynamic-programming and backtracking implementations.
Orientation is local to plan construction; callers never manage numeric
direction values.

## 5. Recompute energy after every seam

**Decision:** Public operations recompute the energy map after each removal.

Removal changes neighboring pixels and can change their energy. Iterative
recomputation therefore matches repeated one-seam operations. A prior
width-based batching heuristic selected different pixels without making that
quality tradeoff explicit.

The private planner retains an explicit batch-size parameter for measurement.
No public fast mode is offered without reproducible evidence and a documented
result contract.

## 6. Keep constants with their owners

**Decision:** Do not maintain a general constants module.

- Gradient border energy lives in the gradient implementation.
- The default highlight color lives with `ResizePlan`.
- CLI directions remain the strings accepted by `argparse`.

The retired `HORIZONTAL` and `VERTICAL` integers had no meaning after the
stateful directional methods were removed. Local ownership makes each value's
scope and compatibility status clear.

## 7. CLI and library boundaries

**Decision:** Keep both an importable library and a command-line interface.

The CLI owns argument parsing, paths, saving, display, logging, and exit behavior.
It maps `resize`, `remove`, and `highlight` commands onto `resize()` and
`plan()`. The command vocabulary remains independent from the Python API shape.

Tradeoff:

- The CLI normalizes a source image before passing an array to a functional
  operation, which may add an owned-array copy. This can be optimized later if
  profiling shows a material cost.

## 8. NumPy-first implementation

**Decision:** Use RGB `uint8` NumPy arrays as the computational representation.

Vectorized row updates, boolean masks, and source-index arrays keep the algorithm
readable while avoiding Python loops over pixels. Array shapes and dtypes remain
runtime invariants because current type annotations do not encode dimensions.

## 9. Versioning during beta

**Decision:** Do not change version `0.5.1` for this internal migration.

The intended distribution has not been released. The final package name and
release version will be chosen during release preparation. Documentation records
the removed beta interface so older local callers have a migration path.

## Deferred work

- Seam insertion and enlargement
- Forward-energy search
- User-selectable resize ordering
- A measured approximate or accelerated mode
- Raw seam and cost-table APIs
- CLI energy plugins
