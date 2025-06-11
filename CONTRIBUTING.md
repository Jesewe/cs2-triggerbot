# Contributing to CS2 TriggerBot

Thank you for your interest in contributing to the CS2 TriggerBot project. This guide will assist you from setting up the development environment to submitting pull requests.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Issues](#submitting-issues)
- [Pull Request Process](#pull-request-process)
- [Feature Requests and Feedback](#feature-requests-and-feedback)

---

## Code of Conduct

By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful, considerate, and open to constructive feedback.

## Getting Started

1. **Fork the Repository**: Create a personal fork of the repository on GitHub.
2. **Clone Your Fork**: Clone your fork to your local environment:

   ```bash
   git clone https://github.com/Jesewe/cs2-triggerbot.git
   cd cs2-triggerbot
   ```

3. **Add Upstream Remote**: Stay updated with the original repository:

   ```bash
   git remote add upstream https://github.com/Jesewe/cs2-triggerbot.git
   ```

## Development Setup

1. **Install Python**: Ensure you have Python version **≥ 3.8** and **< 3.12.5** installed.
2. **Install Dependencies**: Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**: Launch the application for testing and development:

   ```bash
   python main.py
   ```

### Testing Changes

- Execute the application to verify your modifications.
- Review logs at `%LOCALAPPDATA%\Requests\ItsJesewe\crashes\tb_logs.log` for debugging.

## Coding Standards

Adhere to the following guidelines for consistency and readability:

- **PEP 8**: Follow the [PEP 8 style guide](https://www.python.org/dev/peps/pep-0008/).
- **Naming**: Use clear, descriptive names for variables, functions, and classes.
- **Error Handling**: Handle exceptions gracefully and log errors appropriately.
- **Documentation**: Comment complex or critical sections to explain intent.
- **Modularity**: Decompose large functions into smaller, reusable units.

### GUI Development

- **customtkinter**: Use `customtkinter` for any enhancements or changes to the graphical interface.

### Logging

- **Format**: Use the `Logger` class format for log entries.
- **Levels**: Apply appropriate log levels (`INFO`, `WARNING`, `ERROR`) based on severity.

## Submitting Issues

Before submitting a new issue:

1. Search existing issues to avoid duplicates.
2. Provide a clear problem description, steps to reproduce, expected behavior, and relevant logs or screenshots.

## Pull Request Process

1. **Create a Branch**: Use a descriptive branch name:

   ```bash
   git checkout -b feature/your-feature
   ```

2. **Commit Changes**: Ensure each commit message is concise and descriptive:

   ```bash
   git commit -m "Brief description of changes"
   ```

3. **Push to Fork**:

   ```bash
   git push origin feature/your-feature
   ```

4. **Open a Pull Request**: On GitHub, submit a PR to the main repository, including:

   - Purpose of your changes.
   - Potential impact on existing functionality.
   - Testing steps and results.

### Review Process

- **Code Review**: PRs are reviewed for quality, functionality, and adherence to standards.
- **Feedback**: Address requested changes promptly.

## Feature Requests and Feedback

For new ideas or improvements, open an issue labeled **Feature Request** in the [Issues tab](https://github.com/Jesewe/cs2-triggerbot/issues).

We appreciate your contributions to CS2 TriggerBot and your efforts in improving this project!
