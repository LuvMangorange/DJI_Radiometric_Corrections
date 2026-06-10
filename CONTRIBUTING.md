# Contributing to DJI Radiometric Corrections

Thank you for your interest in contributing to DJI Radiometric Corrections! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check the [issues](https://github.com/LuvMangorange/DJI_Radiometric_Corrections/issues) to see if the problem has already been reported.

When reporting a bug, please include:
- **Title**: Clear and concise description of the bug
- **Description**: Detailed explanation of the issue
- **Environment**: 
  - Operating system and version
  - Python version
  - Package versions (run `pip list`)
- **Steps to Reproduce**: Exact steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Screenshots/Logs**: If applicable, include error messages or log output

### Suggesting Features

Feature suggestions are welcome! When proposing a new feature:
1. Use a clear and descriptive title
2. Provide a detailed description of the proposed feature
3. Explain the use case and benefits
4. List any examples or mockups if applicable
5. Note any potential drawbacks or considerations

### Pull Requests

We appreciate pull requests! To contribute code:

#### Step 1: Fork and Clone
```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/DJI_Radiometric_Corrections.git
cd DJI_Radiometric_Corrections
```

#### Step 2: Create a Feature Branch
```bash
# Update main branch
git checkout main
git pull upstream main

# Create a new feature branch
git checkout -b feature/your-feature-name
```

#### Step 3: Make Your Changes
- Follow the project's coding style and conventions
- Write clear, concise commit messages
- Update documentation as needed
- Add or update tests for your changes
- Keep commits focused and atomic

#### Step 4: Test Your Changes
```bash
# Install development dependencies
pip install -r requirements.txt

# Run the test suite
pytest test/ -v

# Check for code quality issues (if linters are configured)
```

#### Step 5: Commit and Push
```bash
# Stage your changes
git add .

# Commit with a clear message
git commit -m "Add feature: description of what was added"

# Push to your fork
git push origin feature/your-feature-name
```

#### Step 6: Create a Pull Request
1. Go to the [repository](https://github.com/LuvMangorange/DJI_Radiometric_Corrections)
2. Click "New Pull Request"
3. Select your feature branch as the "compare" branch
4. Fill in the pull request template:
   - **Title**: Clear description of changes
   - **Description**: What does this PR do? Why?
   - **Related Issues**: Reference any related issues (#123)
   - **Tests**: Describe how you tested the changes
   - **Screenshots**: Include before/after if applicable

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Setting Up Development Environment
```bash
# Clone the repository
git clone https://github.com/LuvMangorange/DJI_Radiometric_Corrections.git
cd DJI_Radiometric_Corrections

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development tools (if applicable)
pip install pytest pytest-cov black flake8
```

## Coding Standards

### Style Guide
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) Python style guidelines
- Use meaningful variable and function names
- Write docstrings for all functions and classes
- Keep lines under 100 characters when possible
- Use type hints for better code clarity

### Example Function Documentation
```python
def black_level_correction(img, bit_num=16, black_level=3200):
    """
    Remove black level offset from sensor images.
    
    Args:
        img (np.ndarray): Input image array
        bit_num (int): Bit depth of the image, default 16
        black_level (int): Black level offset value
        
    Returns:
        np.ndarray: Corrected image with black level removed
        
    Raises:
        ValueError: If black_level is invalid
        TypeError: If img is not an ndarray
    """
```

## Commit Message Guidelines

Use clear, descriptive commit messages:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring without feature changes
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat: Add support for 32-bit image processing

Extend black_level_correction to handle 32-bit depth images
in addition to 16-bit images. This enables processing of
higher precision sensor data.

Closes #42
```

## Testing Guidelines

### Writing Tests
- Add tests for all new features
- Update existing tests if behavior changes
- Aim for good test coverage
- Use descriptive test names

### Running Tests
```bash
# Run all tests
pytest test/ -v

# Run specific test file
pytest test/test_img_arc.py -v

# Run with coverage report
pytest test/ --cov=module --cov-report=html
```

## Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add comments for complex logic
- Update CHANGELOG.md for significant changes

## Pull Request Review Process

1. **Automated Checks**: PRs are checked for code quality and test coverage
2. **Code Review**: At least one maintainer will review your PR
3. **Feedback**: Be responsive to review feedback
4. **Approval**: Once approved, your PR will be merged

## Recognition

Contributors will be recognized in:
- The [README.md](README.md) contributors section
- GitHub's contributor graph
- Release notes for significant contributions

## Questions?

If you have questions or need clarification:
- Check the [documentation](doc/)
- Review existing [issues](https://github.com/LuvMangorange/DJI_Radiometric_Corrections/issues)
- Open a new discussion or issue

## License

By contributing to this project, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to DJI Radiometric Corrections! 🎉
