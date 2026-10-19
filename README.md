# Team Availability Tracker

A small dashboard that lists team members with an availability toggle next to each name. Flipping a toggle updates a boolean value in the database, and the page updates to match: the status label, card styling, summary count and filters all change together.

Built with FastAPI, SQLite and a single-page HTML frontend.

## Features

- Lists all team members with name, role and availability status
- On/off switch per person that saves `is_available` to the database immediately
- Summary at the top showing how many people are available (for example "6 of 9 available") with a progress bar
- Filter tabs: **All**, **Available** and **Unavailable**, each with a live count
- Conditional rendering: available cards are highlighted, unavailable cards are dimmed, and filtered views only show matching people
- Status is shown with a label, a dot style and the switch position, not by colour alone
- Confirmation message after each save, and an error message if saving fails
- Sample team seeded automatically on first run

## Project structure

```
team-availability-tracker/
├── main.py          # FastAPI backend, SQLite DB & API endpoints
├── static/
│   └── index.html   # Dashboard UI
├── .gitignore       # Excludes SQLite database and Python cache
└── README.md        # Documentation
```

## Setup

Requires Python 3.9 or newer.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy
```

## Run

```bash
python main.py
```

Open http://127.0.0.1:8000 in your browser. The database file is created and seeded automatically on first run.

## API endpoints

| Method | Path                              | Description                                   |
| ------ | --------------------------------- | --------------------------------------------- |
| GET    | `/api/users`                      | Returns all team members                      |
| PATCH  | `/api/users/{id}/availability`    | Sets a member's availability and returns them |

Example request:

```http
PATCH /api/users/7/availability
Content-Type: application/json

{ "is_available": false }
```

Example response:

```json
{
  "id": 7,
  "name": "Priya Nair",
  "role": "Data Analyst",
  "is_available": false
}
```

Returns `404` if the user does not exist. Interactive API docs are available at http://127.0.0.1:8000/docs.

## Data model

Table `users`:

| Column         | Type    | Notes                          |
| -------------- | ------- | ------------------------------ |
| `id`           | Integer | Primary key                    |
| `name`         | String  | Required                       |
| `role`         | String  | Required                       |
| `is_available` | Boolean | Defaults to `true`             |

## How it works

1. The page loads and calls `GET /api/users` to render the team list.
2. When a switch is flipped, the frontend sends `PATCH /api/users/{id}/availability` with the new boolean value.
3. The backend updates the row, commits it and returns the saved user.
4. The frontend updates that card from the server response, then recalculates the summary count, progress bar and filter counts.
5. If the active filter no longer matches the person (for example, switching someone off while viewing **Available**), their card is removed from the view.

Because the UI is updated from the server's response, what you see always matches what is stored in the database.

## Notes

- To change the sample team, edit the seed list in `main.py` and delete `team.db` so it is recreated.
- The database file and Python cache are excluded from Git by `.gitignore`.