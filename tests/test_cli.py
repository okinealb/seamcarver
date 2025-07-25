"""
This module tests the command-line interface (CLI) of the seamcarver package,
ensuring that commands like `resize` and `remove` work as expected. It
validates the handling of command-line arguments, logging behavior, and output
to stdout/stderr.

Components Tested:
- CLI commands:
  - `resize`: Resizes an image to specified dimensions.
  - `remove`: Removes a number of seams from an image.
  - `highlight`: Highlights a number of seams in an image.

Dependencies:
- pytest: Used for writing and running the tests.
- os: Used for file path operations.
- tempfile: Used to create temporary files for testing output.
- seamcarver.cli: The main CLI entry point being tested.
"""

# Import standard library packages
import pytest
import os
import tempfile
# Import the project-specific packages
from seamcarver.cli import main

@pytest.fixture
def sample_image():
    """Fixture providing path to sample image."""
    return 'examples/sample.jpg'

@pytest.fixture  
def temp_output():
    """Fixture providing temporary output file path."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)

def test_resize_basic(capsys, sample_image, temp_output):
    """Test basic resize functionality."""
    args = [
        sample_image,
        'resize',
        '200',  # height
        '500',  # width  
        '--output', temp_output
    ]
    main(args)
    
    # Capture the output
    captured = capsys.readouterr()
    
    # Check basic logging 
    assert "Loading image" in captured.err
    assert "Resizing" in captured.err
    assert "Saving" in captured.err
    
    # Check output to stdout
    assert temp_output in captured.err.strip() 
    
    # Verify file was created
    assert os.path.exists(temp_output)

def test_resize_default_output(capsys, sample_image):
    """Test resize with default output filename."""
    args = [
        sample_image,
        'resize', 
        '200',
        '500'
    ]
    main(args)
    
    # Capture the output
    captured = capsys.readouterr()
    
    # Should use default output.jpg
    assert "output.jpg" in captured.err.strip()
    
    # Cleanup
    if os.path.exists("output.jpg"):
        os.unlink("output.jpg")

def test_remove_vertical_seams(capsys, sample_image, temp_output):
    """Test removing vertical seams."""
    args = [
        sample_image,
        'remove',
        '--direction', 'vertical', 
        '--count', '5',
        '--output', temp_output
    ]
    main(args)
    
    # Capture the output
    captured = capsys.readouterr()
    
    # Check basic functionality
    assert "Removing" in captured.err
    assert "vertical" in captured.err
    assert temp_output in captured.err.strip()
    assert os.path.exists(temp_output)

def test_remove_horizontal_seams(capsys, sample_image, temp_output):
    """Test removing horizontal seams.""" 
    args = [
        sample_image,
        'remove',
        '--direction', 'horizontal',
        '--count', '3',
        '--output', temp_output
    ]
    main(args)
    
    # Capture the output
    captured = capsys.readouterr()
    
    assert "Removing" in captured.err
    assert "horizontal" in captured.err
    assert temp_output in captured.err.strip()


def test_remove_default_count(capsys, sample_image, temp_output):
    """Test remove with default count."""
    args = [
        sample_image,
        'remove',
        '--direction', 'vertical',
        '--output', temp_output
    ]
    main(args)
    
    # Capture the output
    captured = capsys.readouterr()
    
    # Should default to 1 seam
    assert "Removing" in captured.err
    assert temp_output in captured.err.strip()


def test_highlight_vertical_seams(capsys, sample_image):
    """Test highlighting vertical seams."""
    args = [
        sample_image,
        'highlight',
        '--direction', 'vertical',
        '--count', '2'
    ]
    main(args)
    
    # Capture the output
    captured = capsys.readouterr()
    
    assert "Highlighting" in captured.err
    assert "vertical" in captured.err


def test_highlight_default_count(capsys, sample_image):
    """Test highlighting with default count."""
    args = [
        sample_image,
        'highlight',
        '--direction', 'horizontal'
    ]
    main(args)
    
    # Capture the output
    captured = capsys.readouterr()
    
    assert "Highlighting" in captured.err
    assert "horizontal" in captured.err

def test_verbose_mode(capsys, sample_image, temp_output):
    """Test verbose logging."""
    args = [
        sample_image,
        '--verbose',
        'resize',
        '200', 
        '500',
        '--output', temp_output
    ]
    main(args)
    
    # Capture the output
    captured = capsys.readouterr()
    
    # Verbose should show more details
    assert "Loading image" in captured.err
    assert temp_output in captured.err.strip()

def test_quiet_mode(capsys, sample_image, temp_output):
    """Test quiet logging."""
    args = [
        sample_image,
        '--quiet',
        'resize',
        '200',
        '500', 
        '--output', temp_output
    ]
    main(args)
    
    # Capture the output
    captured = capsys.readouterr()
    
    # Quiet mode should suppress info messages
    assert "Loading image" not in captured.err

def test_invalid_image_file(capsys):
    """Test error handling for non-existent file."""
    args = [
        'nonexistent.jpg',
        'resize',
        '200',
        '500'
    ]
    
    with pytest.raises(SystemExit) as exc_info:
        main(args)
    
    # Capture the output
    captured = capsys.readouterr()
    
    # Should show error message
    assert captured.err != ""
    assert exc_info.value.code != 0

def test_invalid_dimensions(capsys, sample_image):
    """Test error handling for invalid dimensions."""
    args = [
        sample_image,
        'resize',
        '0',    # Invalid height
        '500'
    ]
    
    with pytest.raises(SystemExit) as exc_info:
        main(args)
    
    # Capture the output
    captured = capsys.readouterr()
    
    # Should show error
    assert captured.err != ""
    assert exc_info.value.code != 0

def test_log_file_output(capsys, sample_image, temp_output):
    """Test logging to a file."""
    log_file = temp_output + '.log'
    
    args = [
        sample_image,
        '--log-file', log_file,
        'resize',
        '200',
        '500',
        '--output', temp_output
    ]
    main(args)
    
    # Capture the output
    captured = capsys.readouterr()
    
    # Should still output result to stdout
    assert temp_output in captured.err.strip()
    
    # Log file should be created
    assert os.path.exists(log_file)
    
    # Cleanup
    if os.path.exists(log_file):
        os.unlink(log_file)