# GitHub Codespaces Guide

Use GitHub Codespaces to run the vBase scripts and notebooks without configuring Python on your computer.

## Configure the API key

Create a Codespaces secret named `VBASE_API_KEY` before opening the codespace:

1. Open your GitHub **Settings**.
2. Select **Codespaces** under **Secrets and variables**.
3. Select **New secret**, enter `VBASE_API_KEY`, paste the key from [vBase Account Settings](https://app.vbase.com/profile/#account_settings), and grant this repository access.

Codespaces exposes the secret as an environment variable. It is separate from an Actions repository secret and does not need a `devcontainer.json` entry.

## Open and prepare the codespace

1. Open the repository on GitHub.
2. Select **Code**, then **Codespaces**, then **Create codespace on main**.
3. In the codespace terminal, install the project and notebook dependencies:

   ```bash
   python -m pip install -r requirements.txt
   python -m pip install jupyterlab
   ```

4. Confirm that the API key is available without printing its value:

   ```bash
   python -c "import os; assert os.getenv('VBASE_API_KEY'); print('VBASE_API_KEY is available')"
   ```

Run a script in the terminal:

```bash
python samples/add_string_dataset_record.py
```

To run a notebook, open a `.ipynb` file under `samples/`, select a Python kernel when prompted, and run its cells in order.

See the [Quickstart](quickstart.md) for AWS and verifier configuration. Never paste secrets into a notebook cell or commit them to the repository.
