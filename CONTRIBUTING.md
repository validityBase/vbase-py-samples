# Contributing to vBase Python Samples

Thank you for considering contributing to vBase Python Samples!

# How to Contribute

## Reporting Issues

If you encounter a bug or have a feature request, please use the GitHub Issues section of the repository to report it:

- Check Existing Issues: Make sure the issue has not already been reported or addressed.
- Create a New Issue: If your issue is new, click the "New Issue" button and select the appropriate template (bug report or feature request).
- Fill Out the Template: Provide as much information as possible to help us understand the problem or feature.

## Making Contributions

To contribute code or documentation, please do the following:

- Create a fork of the repository.
- Create a new branch with your change, and push the changes to it.
- Submit a pull request for your change. Provide a detailed description of the changes and any supporting information.

## Updating Samples and Documentation

- Paired Python and Jupyter samples use percent-format cell markers. After changing a paired `.py` file, run `python scripts/sync_notebooks.py` and commit the generated notebook.
- Run `python -m unittest discover -s tests -v` before opening a pull request.
- Keep notebook outputs and execution counts cleared.
- Never commit API keys, cloud credentials, private keys, or real account data.
- Use MyST-compatible Markdown. Keep explicit heading IDs aligned with the heading text and update links when headings change.
- Install the locked Node dependencies with `npm ci --ignore-scripts` before running Prettier locally.
