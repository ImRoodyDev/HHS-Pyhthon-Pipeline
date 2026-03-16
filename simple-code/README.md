# Python Setup Guide (simple-code)

This README explains how to set up Python for the `simple-code` folder on Windows (PowerShell).

## 1) Open the project folder

Open PowerShell in:

`D:\User\Documents\Developments\Softwares\Python\HHS_Study`

## 2) Check Python installation

Run:

```powershell
python --version
```

If this fails, install Python 3.13+ from python.org and reopen PowerShell.

## 3) Create a virtual environment

From the project root:

```powershell
python -m venv env
```

## 4) Activate the virtual environment

```powershell
& .\env\Scripts\Activate.ps1
```

You should see `(env)` in your terminal prompt.

## 4.1) Connect to `(env)`

To connect to the virtual environment in a new terminal, run:

```powershell
& .\env\Scripts\Activate.ps1
```

If successful, your prompt starts with `(env)`.

## 4.2) Disconnect from `(env)`

To leave the virtual environment, run:

```powershell
deactivate
```

After this, `(env)` disappears from the prompt.

## 5) Upgrade pip (recommended)

```powershell
python -m pip install --upgrade pip
```

## 6) Install dependencies

If `requirements.txt` exists:

```powershell
python -m pip install -r requirements.txt
```

Or install manually:

```powershell
python -m pip install pandas openpyxl jupyter ipykernel
```

## 7) Verify installation

```powershell
python --version
python -m pip --version
python -c "import pandas; print(pandas.__version__)"
```

## 8) Run scripts in `simple-code`

```powershell
python .\simple-code\main.py
python .\simple-code\logger.py
```

## 9) (Optional) Save installed packages

```powershell
python -m pip freeze > requirements.txt
```

---

## Troubleshooting

### `pip` launcher fatal error

If you get a launcher path error, repair pip with:

```powershell
python -m pip install --upgrade --force-reinstall pip
```

Then use `python -m pip ...` commands.

### PowerShell script execution policy error

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Restart terminal and activate again.
