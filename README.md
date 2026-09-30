# PocketSmart AI — Scenario 3 Prototype

Jewelry Recommendations for Occasions.

## Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python Flask
- Database: SQLite
- AI: Prototype recommendation engine; Gemini can be connected in the next step

## Run in VS Code

1. Open this folder in VS Code.
2. Open Terminal.
3. Create a virtual environment (optional but recommended):

   Windows:
   `python -m venv venv`
   `venv\Scripts\activate`

   macOS/Linux:
   `python3 -m venv venv`
   `source venv/bin/activate`

4. Install:
   `pip install -r requirements.txt`

5. Start:
   `python app.py`

6. Open the address shown by Flask, usually:
   `http://127.0.0.1:5000`

## What is already implemented
- Budget input
- Occasion selection
- Style selection
- Outfit image upload
- Recommendation logic
- Budget total and remaining amount
- SQLite database storage
- Recent plans/history
- Responsive UI suitable for prototype/demo

## Next upgrade
Replace the prototype `recommend()` function in `app.py` with a Gemini API call for real outfit/image analysis and AI-generated recommendations. Then connect real product/catalog data or approved affiliate/product APIs.
