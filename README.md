# seam_carving
A command-line Python tool for image resizing using seam carving.

We calculate the energy of each pixel by first finding the gradient magnitude. Then, by summing the squares and square rooting the result, we can determine the lowest energy seam — i.e., the path of lowest difference. Finally we remove the seams as needed, resulting in ["content-aware image resizing"](https://en.m.wikipedia.org/wiki/Seam_carving).

Note: Currently only for removing seams by gradient magnitude.

## Installation
```bash
$ pip install seam_carving
```
