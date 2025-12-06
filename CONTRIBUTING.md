# Contributing to Real-Time Fraud Detection Pipeline

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. Check existing issues to avoid duplicates
2. Use the latest version of the code
3. Verify the bug is reproducible

When reporting a bug, include:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Logs or error messages
- Screenshots if applicable

### Suggesting Enhancements

When suggesting features:
1. Check if it's already suggested
2. Explain the use case clearly
3. Provide examples if possible
4. Consider backward compatibility

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/Timmisetty1/Real-Time-Fraud-Detection-Pipeline.git
   cd Real-Time-Fraud-Detection-Pipeline
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new features
   - Update documentation as needed

4. **Run tests**
   ```bash
   pytest tests/ -v
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Use a clear title
   - Describe what changed and why
   - Reference related issues
   - Include test results

## Development Setup

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Timmisetty1/Real-Time-Fraud-Detection-Pipeline.git
cd Real-Time-Fraud-Detection-Pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (if added)
pip install pytest pytest-cov black flake8 mypy
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_feature_extractor.py -v
```

### Code Style

We follow PEP 8 guidelines:

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/
```

## Project Structure

```
.
├── src/                    # Source code
│   ├── data_ingestion/    # Kafka consumer/producer
│   ├── feature_engineering/  # Feature extraction
│   ├── model/             # ML models
│   ├── scoring/           # Scoring service
│   ├── monitoring/        # Metrics and monitoring
│   ├── pipeline.py        # Main pipeline
│   └── api.py            # REST API
├── tests/                 # Unit tests
├── scripts/              # Utility scripts
├── config/               # Configuration files
├── data/                 # Sample data
└── docs/                 # Documentation
```

## Coding Guidelines

### Python Style

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for classes and functions
- Keep functions small and focused
- Use meaningful variable names

Example:
```python
def extract_features(self, transaction: Dict) -> Dict:
    """
    Extract features from a transaction.
    
    Args:
        transaction: Raw transaction data
        
    Returns:
        Dictionary of extracted features
    """
    features = {}
    # Implementation
    return features
```

### Testing

- Write tests for new features
- Maintain or improve code coverage
- Use descriptive test names
- Test edge cases

Example:
```python
def test_feature_extraction_with_missing_fields():
    """Test feature extraction handles missing fields gracefully"""
    extractor = FeatureExtractor({})
    transaction = {'transaction_id': 'tx1'}  # Missing required fields
    
    features = extractor.extract_features(transaction)
    
    assert 'amount' in features
    assert features['amount'] == 0  # Default value
```

### Documentation

- Update README.md for user-facing changes
- Update ARCHITECTURE.md for design changes
- Add inline comments for complex logic
- Keep docstrings up to date

## Areas for Contribution

### High Priority
- [ ] Improve model accuracy with real datasets
- [ ] Add more feature engineering techniques
- [ ] Implement explainable AI (SHAP values)
- [ ] Add integration tests
- [ ] Improve error handling

### Medium Priority
- [ ] Add support for more ML frameworks (TensorFlow, PyTorch)
- [ ] Implement model versioning
- [ ] Add A/B testing framework
- [ ] Create Grafana dashboards
- [ ] Add more comprehensive logging

### Nice to Have
- [ ] Web UI for monitoring
- [ ] Additional example datasets
- [ ] Performance benchmarks
- [ ] Multi-language support
- [ ] Mobile app integration examples

## Review Process

1. **Automated checks**: CI/CD runs tests and linters
2. **Code review**: Maintainers review code
3. **Testing**: Manual testing if needed
4. **Approval**: At least one maintainer approval required
5. **Merge**: Squash and merge to main branch

## Release Process

1. Version bump in `setup.py`
2. Update CHANGELOG.md
3. Create release branch
4. Tag release
5. Deploy to PyPI (if applicable)

## Questions?

Feel free to:
- Open an issue for questions
- Join discussions
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Acknowledgments

Thank you to all contributors who help make this project better!
