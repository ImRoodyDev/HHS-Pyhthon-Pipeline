# How to Create a Jupyter Notebook for Python

This guide shows how to create and run a Python Jupyter Notebook in VS Code.

## 1) Open the project

- Open VS Code.
- Open folder: `HHS_Study`.

## 2) Activate your Python environment

In the terminal, run:

```powershell
& .\env\Scripts\Activate.ps1
```

If your environment does not exist yet, create one first:

```powershell
python -m venv env
& .\env\Scripts\Activate.ps1
```

## 3) Install Jupyter packages

With the environment active, run:

```powershell
pip install jupyter ipykernel
```

## 4) Create a notebook in VS Code

- In the Explorer, right-click the folder where you want it.
- Select **New File**.
- Name it something like: `analysis.ipynb`.
- Open the file.

## 5) Select the Python kernel

- At the top-right of the notebook, click **Select Kernel**.
- Choose the interpreter from your `env` virtual environment.

## 6) Add and run cells

Example first cell:

```python
import pandas as pd
print("Jupyter is ready")
```

- Press **Shift+Enter** to run a cell.
- Use **+ Code** to add more cells.

## 7) Save and share

- Press **Ctrl+S** to save the notebook.
- Notebook files are saved as `.ipynb`.

---

## Optional: Start notebook from terminal

You can also launch Jupyter in the browser:

```powershell
jupyter notebook
```

Then create a new Python notebook from the web UI.

## Common issues

- **Kernel not found**: Re-select kernel and choose your `env` interpreter.
- **Module not found**: Install package into active env, e.g. `pip install pandas`.
- **PowerShell execution policy error**: run PowerShell as admin once and use:

```powershell
Set-ExecutionPolicy RemoteSigned
```
