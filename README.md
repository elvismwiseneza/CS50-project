# Campus Tech Help Desk Lite
#### Video Demo: <ADD YOUR VIDEO URL HERE>
#### Description:

Campus Tech Help Desk Lite is a small web app made for my CS50 final project. It helps students or staff report simple tech problems on campus. For example, someone can report weak Wi-Fi, a broken projector, a computer that is not working, or an account access problem.

The app is small on purpose. I wanted to build something real, useful, and easy to finish well. A user fills out a short form with a title, location, category, and details. After the form is submitted, the issue is saved in a SQLite database and shown on the page. The user can view open issues, resolved issues, or all issues. If a problem is fixed, the user can click a button to mark it as resolved.

This project uses Python, JavaScript, and SQL, which matches the first project idea from the CS50 page. I used Python for the backend, JavaScript for the interactive parts of the page, and SQLite for storing data. I kept the stack simple so the project is easier to understand and easier to explain in a short video.

The main file is `app.py`. This file starts the web server, creates the database table if needed, and handles the app routes. It also serves the website files and the API routes. The main API routes are `GET /api/issues`, `POST /api/issues`, and `POST /api/issues/<id>/resolve`.

The file `templates/index.html` contains the page structure. It has the heading, the issue form, the filter buttons, and the area where issues appear. The file `static/app.js` handles the frontend behavior. It sends data to the backend, loads issues from the server, changes the filter, and marks issues as resolved. The file `static/styles.css` controls the colors, layout, buttons, cards, and mobile view.

The `data` folder stores the SQLite database when the app runs. I chose SQLite because it is simple and does not need extra setup. The file `tests/test_app.py` contains a few small tests. These tests check that a new issue can be created and that an issue can be marked as resolved. I included tests because they help show that the main features work.

I thought about adding more features like user accounts, priorities, comments, or delete buttons. I decided not to do that because the project would become too large. I wanted a clean mini help desk, not a full ticket system. Keeping the scope small helped me finish the project in a polished way.

To run the project, open a terminal in `C:\Users\Bench06\Documents\CS50 project` and run `py app.py`. Then open `http://127.0.0.1:8000` in your browser. The database file will be created automatically the first time the app starts. No extra packages are needed.

