# PDF Editor Web App - Quick Start Guide

## ✅ Setup Complete!

Your virtual environment has been configured and all dependencies are installed.

## 🚀 Running the Application

### Option 1: Double-click the batch file
Simply double-click `START_SERVER.bat` to launch the application.

### Option 2: Manual start (PowerShell)
```powershell
cd 'C:\Users\jehu.peters\OneDrive - Seven Oaks School Division\2025-2026\PDF program\PDF-Editor'
.\venv\Scripts\Activate.ps1
python app.py
```

### Option 3: Manual start (Command Prompt)
```cmd
cd "C:\Users\jehu.peters\OneDrive - Seven Oaks School Division\2025-2026\PDF program\PDF-Editor"
venv\Scripts\activate.bat
python app.py
```

## 🌐 Accessing the Application

Once the server starts, you'll see:
```
* Running on http://127.0.0.1:5000
```

Open your web browser and go to: **http://localhost:5000**

## 📝 Using the Application

1. **Upload PDFs**: Drag and drop or click to select PDF files
2. **Edit**: View all pages in a grid, click to select/deselect
3. **Delete Pages**: Click the X on any page thumbnail
4. **Download**: Click "Merge & Download" to get your final PDF

## 🛑 Stopping the Server

Press `CTRL+C` in the terminal window to stop the Flask server.

## 🔧 Troubleshooting

### Port Already in Use
If you see "Address already in use", stop any other Flask servers or change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed from 5000
```

### Module Not Found Errors
Make sure the virtual environment is activated (you should see `(venv)` in your terminal prompt).

### Permission Errors
Run PowerShell as Administrator if you encounter permission issues.

## 📦 Installed Packages

- Flask 3.1.0
- PyMuPDF (fitz) - For PDF rendering
- PyPDF2 - For PDF manipulation

## 🧹 Cleanup Old Files

The application automatically stores temporary files in `instance/uploads/{session_id}/`.

To manually clean up:
```powershell
.\venv\Scripts\Activate.ps1
python cleanup.py
```

## 📚 Additional Documentation

- **Deployment**: See `PYTHONANYWHERE_DEPLOYMENT.md` for hosting instructions
- **Migration Details**: See `MIGRATION_SUMMARY.md` for architecture overview
- **Original Features**: Check existing README files for feature documentation

## 🎯 Next Steps

For production deployment on PythonAnywhere, follow the guide in `PYTHONANYWHERE_DEPLOYMENT.md`.
