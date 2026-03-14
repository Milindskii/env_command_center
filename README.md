# Environment Command Center (Backend)

Welcome to the backend for the Environment Command Center! This FastAPI application monitors Air Quality, Noise Pollution, and Sound Levels.

## 📂 Understanding the Folder Structure

Don't be overwhelmed by the files! Everything is organized to keep the code **safe, clean, and fast**. Here's what everything does:

### 1. The Core Application (`app/` folder)
* **`main.py`**: The entry point. It starts the server, connects to the database, and loads the routes.
* **`core/config.py`**: Handles environment variables (like passwords). It reads from the `.env` file so you don't hardcode secrets.

### 2. The Database (`db/`, `models/`, `schemas/` folders)
* **`db/session.py`**: Connects your code to PostgreSQL.
* **`models/`**: Defines what the database tables look like (`air.py`, `noise.py`). This is the **Database Layer**.
* **`schemas/`**: Pydantic rules that check if data coming in or out is correct (e.g. "AQI must be a number > 0"). This is the **Validation Layer**.

### 3. The Features (`routes/`, `services/` folders)
* **`routes/`**: The "URLs" you visit (like `/environment/air`). Routes act like traffic cops: they get requests, pass them to services, and return responses to the user.
* **`services/`**: The "Brains". This handles the actual database queries, fetches data from APIs (like `aqi_client.py`), and does math (like `analytics.py`).

### 4. Background Tasks (`scheduler/` folder)
* **`jobs.py` & `updater.py`**: Runs automatically every 10 minutes to fetch new API data, and runs daily to delete old data so your database doesn't get flooded.

---

## 🔒 Keeping Hackers Out (API Keys & Passwords)

** NEVER WRITE PASSWORDS DIRECTLY IN CODE!**

We use a `.env` file to keep your API keys and database password safe.
There is a `.gitignore` file included that tells `git` to purely **ignore** your `.env` file. This means when you push to GitHub, your password stays safe on your local computer.

1. Open the `.env` file in the root of the backend.
2. Update it with your secret information:
```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/env_command_center
AQI_API_KEY=your_real_api_key_from_aqicn_org
```
3. Because of the `.gitignore`, Git will never upload this file.
4. The backend limits requests using `slowapi` so bad actors can't spam your endpoints and crash your server.

---

## 🚀 How to Run the Server

Start the application safely using this command inside the `backend/` folder:

```bash
py -m uvicorn app.main:app --reload
```

Then visit:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** to see all your available interactive API endpoints!
