# Contributing to the Hybrid Movie Recommendation System

Thank you for your interest in contributing to this project! We welcome contributions from developers of all skill levels. By participating in this project, you agree to abide by our Code of Conduct.

## How Can I Contribute?

### Reporting Bugs
*   Ensure the bug was not already reported by searching on GitHub under Issues.
*   If you're unable to find an open issue addressing the problem, open a new one. Be sure to include a title and clear description, as much relevant information as possible, and a code sample or an executable test case demonstrating the expected behavior that is not occurring.

### Suggesting Enhancements
*   Open a new issue with a clear title and detailed description.
*   Explain why this enhancement would be useful to most users.

### Pull Requests
1.  Fork the repo and create your branch from `main`.
2.  If you've added code that should be tested, add tests.
3.  If you've changed APIs or features, update the documentation.
4.  Ensure the test suite passes (`pytest test_app.py`).
5.  Make sure your code matches the existing style (we use `black` for formatting).
6.  Issue that pull request!

## Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/DARREN-2000/Hybrid-Movie-Recommendation-System.git
    cd Hybrid-Movie-Recommendation-System
    ```
2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    pip install pytest black  # For testing and formatting
    ```
4.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## Submitting Changes
*   Push your changes to a topic branch in your fork of the repository.
*   Submit a pull request to the `main` branch.
*   Update the PR description to clearly explain the changes and the problem they solve.

Thank you for helping make this project better!
