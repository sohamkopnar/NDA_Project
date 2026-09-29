NDA PREP - LOCAL SETUP (WINDOWS)
================================

1. Extract the complete NDA_Project folder from the ZIP.
2. Open that folder in Visual Studio Code.
3. Open Terminal > New Terminal.
4. (Recommended) Create a virtual environment:
      py -m venv .venv
      .venv\Scripts\activate
5. Install dependencies:
      py -m pip install -r requirements.txt
6. Start the site:
      py app.py
7. Open this address in your browser:
      http://127.0.0.1:5000
8. Register an account to access the dashboard and study features.

The SQLite database (database.db) is created automatically on first run.
To reset all local accounts and test history, stop the app and delete database.db.

NOTES
- Keep app.py, templates/, static/, and requirements.txt together in the same folder.
- This is a local learning project. Before public deployment, set a secure NDA_SECRET_KEY,
  disable Flask debug mode, and configure production hosting.
- Practice questions are NDA-style originals, not a verified archive of official UPSC papers.
