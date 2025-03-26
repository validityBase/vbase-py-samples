---
title: GitHub Codespaces Guide
---

<!-- omit in toc -->
# GitHub Codespaces Guide

This tutorial guides you through setting up GitHub Codespaces to run vBase samples.

- [1. Open a Notebook in GitHub Codespaces](1-open-a-notebook-in-github-codespaces)
- [2. Configure Codespaces Secrets](2-configure-codespaces-secrets)
  - [2.1. Add the Secret to GitHub Repository Secrets](21-add-the-secret-to-github-repository-secrets)
  - [2.2. Use the Secret in Your Codespace](22-use-the-secret-in-your-codespace)

(1-open-a-notebook-in-github-codespaces)=
## 1. Open a Notebook in GitHub Codespaces<a href="#1-open-a-notebook-in-github-codespaces" id="1-open-a-notebook-in-github-codespaces"></a>

To open a Jupyter notebook from a public GitHub repository in GitHub Codespaces, follow these steps:

1. **Create a Codespace:**
   - Navigate to the repository in GitHub.
   - Click on the `Code` button and then select `Open with Codespaces`.
   - If you don't have a Codespace created for the repository, click on `New codespace` to create one.

2. **Set Up the Codespace:**
   - Once the Codespace is created and running, open the terminal in Codespaces.
   - Ensure that you have Jupyter installed. If not, you can install it by running:
     ```bash
     pip install notebook
     ```

3. **Navigate to the Notebook:**
   - In the file explorer on the left side of the Codespace, navigate to the directory where your Jupyter notebook (.ipynb file) is located.
   - Click on the notebook file to open it.

4. **Run the Jupyter Notebook Server:**
   - In the terminal, navigate to the directory containing your notebook and start the Jupyter notebook server by running:
     ```bash
     jupyter notebook
     ```
   - This will start the Jupyter server and provide a URL to open the notebook in your browser.

5. **Open the Notebook in Browser:**
   - Copy the provided URL from the terminal and paste it into your browser.
   - You should see the Jupyter notebook interface with your notebook file opened and ready to use.

(2-configure-codespaces-secrets)=
## 2. Configure Codespaces Secrets<a href="#2-configure-codespaces-secrets" id="2-configure-codespaces-secrets"></a>

To configure an environment variable in GitHub Codespaces that contains a secret you do not want to save directly in your repository, you can use GitHub's secrets management feature. Here's how you can achieve this:

(21-add-the-secret-to-github-repository-secrets)=
### 2.1. Add the Secret to GitHub Repository Secrets<a href="#21-add-the-secret-to-github-repository-secrets" id="21-add-the-secret-to-github-repository-secrets"></a>

1. **Navigate to Your Repository:**
   - Go to your repository on GitHub.

2. **Access Repository Settings:**
   - Click on the `Settings` tab of your repository.

3. **Add a New Secret:**
   - In the left sidebar, click on `Secrets and variables` and then `Actions`.
   - Click on the `New repository secret` button.
   - Add your secret with a name and its value. For example, you can name it `MY_SECRET` and provide the secret value.

(22-use-the-secret-in-your-codespace)=
### 2.2. Use the Secret in Your Codespace<a href="#22-use-the-secret-in-your-codespace" id="22-use-the-secret-in-your-codespace"></a>

To use the secret within your Codespace, you'll need to reference it in your `devcontainer.json` file.

1. **Edit/Create `devcontainer.json`:**
   - Open your repository in GitHub Codespaces.
   - Navigate to the `.devcontainer` directory and open (or create) the `devcontainer.json` file.

2. **Reference the Secret:**
   - Modify the `devcontainer.json` to use the secret. Here’s an example configuration:
   
     ```json
     {
       "name": "My Codespace",
       "image": "mcr.microsoft.com/vscode/devcontainers/python:3.8",
       "containerEnv": {
         "MY_SECRET": "${{ secrets.MY_SECRET }}"
       },
       "settings": {
         "terminal.integrated.shell.linux": "/bin/bash"
       },
       "extensions": [
         "ms-python.python",
         "ms-azuretools.vscode-docker"
       ],
       "postCreateCommand": "echo 'Codespace setup complete!'"
     }
     ```

3. **Rebuild the Container:**
   - After making these changes, rebuild your Codespace container.
   - Open the command palette (`F1` or `Ctrl+Shift+P` on Windows/Linux, `Cmd+Shift+P` on macOS) and type `Codespaces: Rebuild Container`, then select it.

4. **Verify the Secret:**
   - Open a terminal in your Codespace and check if the secret environment variable is set:
     ```bash
     echo $MY_SECRET
     ```
   - Once the secrets verify you can use them as ordinary environment variables to initialize your vBase client.
