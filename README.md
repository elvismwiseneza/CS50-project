# Campus Tech Help Desk Lite
#### Video Demo: <ADD YOUR VIDEO URL HERE>
#### Description:

Campus Tech Help Desk Lite is a small web app for reporting simple tech problems on a school campus. A user can report issues like bad Wi-Fi, a broken projector, a lab computer problem, or an account access issue. Each report is saved in a SQLite database and shown on the page. The user can view open issues, resolved issues, or all issues, and can mark an issue as resolved with one click.

I made this project with Python, JavaScript, and SQL for my CS50 final project. I wanted something small, useful, and easy to understand. The goal was not to build a full ticket system. The goal was to build a clean mini help desk that works well and shows the main ideas of full stack web development.

The main backend file is `app.py`. It starts the web server, creates the database table if needed, and handles the API routes. The main routes are `GET /api/issues`, `POST /api/issues`, and `POST /api/issues/<id>/resolve`. The page structure is in `templates/index.html`. The frontend logic is in `static/app.js`, which sends requests and updates the page. The design is in `static/styles.css`. The `data` folder holds the SQLite database when the app runs. The file `tests/test_app.py` has a few tests for creating and resolving issues.

I made a few simple design choices on purpose. I used SQLite because it is easy to set up and works well for a small project. I used plain JavaScript and plain CSS so the code stays short and readable. I did not add logins, priorities, or comments because that would make the project much bigger. Keeping the scope small helped me finish a working project that I can explain clearly.

To run the project from GitHub on any computer:

```bash
git clone <your-repo-url>
cd <your-repo-folder>
python app.py
```

Then open `http://127.0.0.1:8000` in a browser.

You can also run the app with Docker:

```bash
docker build -t campus-help-desk-lite .
docker run -p 8000:8000 campus-help-desk-lite
```

Then open `http://127.0.0.1:8000`.

This app now uses the `HOST` and `PORT` environment variables, so it can run on other machines and on a hosting service, not only on my computer. GitHub stores the code, but GitHub alone does not run Python web apps for visitors. To make it live for everyone online, this repo can be deployed on any service that supports Python or Docker. I also added a `render.yaml` file so the repo is ready for Render deployment.

I also added AI notes in the code comments because CS50 allows AI tools as helpers for the final project, as long as the work and understanding are still my own.
