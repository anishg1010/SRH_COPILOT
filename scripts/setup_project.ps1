Write-Host "Creating virtual environment..."
python -m venv venv

Write-Host "Activating environment..."
.\venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
pip install -r requirements.txt

Write-Host "Setup complete."
