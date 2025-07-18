# seamcarver
A command-line Python tool for image resizing using seam carving.

We calculate the energy of each pixel by first finding the gradient magnitude. Then, by summing the squares and square rooting the result, we can determine the lowest energy seam — i.e., the path of lowest difference. Finally we remove the seams as needed, resulting in ["content-aware image resizing"](https://en.m.wikipedia.org/wiki/Seam_carving).

Note: Currently only for removing seams by gradient magnitude.

## Installation
```bash
$ pip install seamcarver
```

## Package structure
```
seamcarver/             # Project root directory
├── seamcarver/         # Main package source code
│   ├── __init__.py     # Package initializer
│   ├── cli.py          # Command-line interface
│   ├── core.py         # Core seam carving logic
│   ├── calculator.py   # Energy calculation utilities
│   ├── constants.py    # Internal constants
│   ├── utils.py        # Helper functions
│   └── methods/        # Energy interface and methods
├── tests/              # Unit tests for the package
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Build system and metadata
├── .gitignore          # Git ignore rules
├── LICENSE             # License information
└── README.md           # Project documentation
```