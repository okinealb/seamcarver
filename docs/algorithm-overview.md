# Algorithm Overview

This document explains how seam selection and seam removal are implemented in the current codebase.

## 1. Goal

The algorithm finds low-energy connected pixel paths (seams) and removes or highlights them while trying to preserve visually important content (`seamcarver/core.py:136-160`, `seamcarver/calculator.py:27-33`).

## 2. Inputs and outputs

- **Input image**: `SeamCarver` owns an RGB `uint8` NumPy array with shape
  `(H, W, 3)`. NumPy inputs must already use that representation and are copied.
  Integer nested lists are range-checked and converted. PIL images and filesystem
  paths are converted to RGB (`src/seamcarver/_image.py`, `normalize_image`).
- **Control inputs**:
  - operation (`resize`, `remove`, `highlight`) (`seamcarver/core.py:125-160`)
  - direction (`VERTICAL` or `HORIZONTAL`) (`seamcarver/constants.py:10-13`)
  - number of seams (`num_seams`), which must satisfy
    `1 <= num_seams < oriented dimension`
- **Output from seam finder**: boolean seam mask `(H, W)` where `True` denotes seam pixels (`seamcarver/calculator.py:93-95`, `123-127`).

## 3. Direction handling

Only vertical seam logic is implemented in the calculator. `SeamCarver` creates a
local transposed view for horizontal requests and stores the completed result only
after processing succeeds (`src/seamcarver/core.py`, `_orient_image`).

## 4. Energy-map generation

`SeamCalculator` delegates energy computation to an injected `EnergyMethod` strategy (`seamcarver/calculator.py:67-75`, `179-183`, `seamcarver/methods/interface.py:13-35`).

Built-in energy methods:

1. **GradientEnergy**: interior gradient magnitude + fixed border energy (`seamcarver/methods/gradient.py:23-31`, `seamcarver/constants.py:14-15`)
2. **SobelEnergy**: grayscale conversion + Sobel gradients (`seamcarver/methods/sobel.py:26-30`)
3. **LaplacianEnergy**: grayscale conversion + Laplacian magnitude (`seamcarver/methods/laplacian.py:26-29`)

## 5. Dynamic-programming cumulative costs

For each candidate seam, cumulative minimum costs are computed row-by-row:

- Initialize `costs` from `energy` (`seamcarver/calculator.py:188-190`)
- For each row, add the minimum reachable predecessor from the previous row (`seamcarver/calculator.py:192-199`)
  - interior: min of left-up, up, right-up
  - boundaries: min of valid neighbors

This produces a cumulative table where the minimum in the last row is the seam endpoint (`seamcarver/calculator.py:210-212`).

## 6. Seam backtracking

Backtracking starts from the minimum-cost pixel in the last row and walks upward by choosing the minimum predecessor in `[prev-1, prev, prev+1]` (`seamcarver/calculator.py:223-227`).

During backtracking:

- seam pixels are marked in a boolean mask (`seamcarver/calculator.py:208`, `218`, `234`)
- selected pixels are invalidated in `energy` by setting them to `np.inf` (`seamcarver/calculator.py:219`, `235`)
- if no valid finite path exists, `SeamExhausedException` is raised (`seamcarver/calculator.py:214-216`, `230-232`)

## 7. Multi-seam extraction flow

For a call requesting `num_seams`:

1. The image is copied, and an index map (`kept`) is initialized (`seamcarver/calculator.py:101-107`).
2. `_process` repeatedly computes one seam at a time from the current energy state until successful count reaches target or exhaustion (`seamcarver/calculator.py:129-155`).
3. Found seams are removed from the working image via boolean mask reshape (`seamcarver/calculator.py:118-122`).
4. Final seam coordinates are reconstructed in original image space by inverting the kept-mask (`seamcarver/calculator.py:123-127`).

## 8. Applying seams to user operations

- **Remove**: drop seam pixels and reshape to reduce width by seam count (`seamcarver/core.py:145-148`).
- **Highlight**: color seam pixels without removing them (`seamcarver/core.py:159-160`, `seamcarver/constants.py:16-17`).
- **Resize**: shrink one or both dimensions, or leave them unchanged. Enlargement
  is rejected until seam addition is implemented. A failed resize restores the
  original image.
- **Add**: explicitly raises `NotImplementedError`; seam addition remains deferred.

## 9. Complexity summary

For one seam on an image of height `H` and width `W`:

- energy computation: method-dependent, typically `O(HW)` (`seamcarver/methods/gradient.py:23-31`, `seamcarver/methods/sobel.py:26-30`, `seamcarver/methods/laplacian.py:26-29`)
- cumulative costs: `O(HW)` (`seamcarver/calculator.py:192-199`)
- backtracking: `O(H)` (`seamcarver/calculator.py:223-239`)

For `k` seams, cost scales roughly with repeated seam extraction and periodic image compaction (`seamcarver/calculator.py:112-122`, `143-150`).
