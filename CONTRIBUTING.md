# Contributing to CS2 TriggerBot

Thank you for your interest in contributing to the CS2 TriggerBot project! This guide will help you get started with contributing, from setting up the development environment to submitting pull requests.

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

By participating in this project, you agree to abide by the project's [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful, considerate, and open to constructive feedback.

## Getting Started

1. **Fork the Repository**: Create a personal fork of the repository on GitHub.
2. **Clone Your Fork**: Clone your fork to your local development environment.
   ```bash
   git clone https://github.com/Jesewe/cs2-triggerbot.git
   cd cs2-triggerbot
   ```
3. **Set Up a Remote**: Add the original repository as an upstream remote to stay updated with the latest changes.
   ```bash
   git remote add upstream https://github.com/Jesewe/cs2-triggerbot.git
   ```

## Development Setup

1. **Install Python**: Ensure you have Python 3.8 or later installed.
2. **Install Dependencies**: Install the required Python packages.
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Application**: You can start the application for testing and development with:
   ```bash
   python main.py
   ```

### Testing Changes
- Run the application to ensure any changes you make are functioning as expected.
- Check logs in `%LOCALAPPDATA%\Requests\ItsJesewe\crashes\tb_logs.log` for debugging information.

## Coding Standards

Please follow these guidelines to ensure consistency and readability in the codebase:

- **PEP 8 Style Guide**: Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code.
- **Naming Conventions**: Use clear and descriptive names for variables, functions, and classes.
- **Error Handling**: Handle exceptions gracefully and log errors to help users debug issues.
- **Code Comments**: Include comments for complex or critical sections of code to explain their purpose.
- **Modularization**: Break down larger functions into smaller, reusable functions when possible.

### GUI Development
- **PyQt6**: Use `PyQt6` for any updates or improvements related to the graphical interface.
- **Consistent Styling**: Follow the existing CSS styles for GUI components in the `MainWindow` class.

### Logging
- **Logging Format**: Use the format defined in the `Logger` class for consistency in log entries.
- **Log Levels**: Use appropriate log levels (`INFO`, `WARNING`, `ERROR`) based on the severity of the message.

## Submitting Issues

Before opening a new issue, please:
1. Search for existing issues to avoid duplicates.
2. Clearly describe the problem, including steps to reproduce, expected behavior, and any relevant logs or screenshots.

## Pull Request Process

1. **Create a New Branch**: Use a descriptive branch name that indicates the purpose of the changes.
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Commit Your Changes**: Make sure each commit message is clear and concise.
   ```bash
   git commit -m "Brief description of your changes"
   ```

3. **Push to Your Fork**: Push your changes to your fork on GitHub.
   ```bash
   git push origin feature/your-feature
   ```

4. **Submit a Pull Request**: Go to the main repository on GitHub and submit a pull request from your branch. Make sure to provide a detailed description of your changes, including:
   - The purpose of the changes.
   - Any potential impact on existing functionality.
   - How you tested the changes.

### Pull Request Review
- **Code Review**: Pull requests will be reviewed for quality, functionality, and adherence to the coding standards.
- **Changes Requested**: You may be asked to make changes before the pull request can be merged. Please address feedback promptly.

## Feature Requests and Feedback

If you have ideas for new features or improvements, please open an issue with the **Feature Request** label in the [Issue](https://github.com/Jesewe/cs2-triggerbot/issues) tab.

Thank you for contributing to CS2 TriggerBot and helping make this project better!
