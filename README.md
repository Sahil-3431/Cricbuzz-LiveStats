# 🏏 Cricbuzz LiveStats

A Streamlit-based cricket analytics dashboard that combines real-time cricket data from the Cricbuzz API with SQLite database analytics and CRUD operations.

## 🚀 Project Overview

**Cricbuzz LiveStats** is an interactive cricket analytics application built using Python, Streamlit, SQLite and the Cricbuzz API through RapidAPI.

The application provides:

* 🏏 Live cricket matches
* 📊 Player batting and bowling statistics
* 🗄️ SQL-based cricket analytics
* ✏️ CRUD operations
* 📈 Match and player insights
* 🖼️ Player images
* 🗃️ SQLite database integration

## 🛠️ Technologies Used

* Python
* Streamlit
* Pandas
* Requests
* SQLite
* SQL
* RapidAPI
* Cricbuzz API

## 📁 Project Structure

```text
Cricbuzz-Project/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── assets/
│   └── players/
│
├── database/
│   └── cricbuzz.db
│
├── pages/
│   ├── 1_Live_Matches.py
│   ├── 02_Top_Player_Stats.py
│   ├── 03_SQL_Analytics.py
│   └── 04_CRUD.py
│
└── utils/
    ├── api_client.py
    └── db_connection.py
```

## ✨ Features

### 🏏 Live Matches

The Live Matches page retrieves currently available cricket matches through the Cricbuzz API.

It provides:

* Match status
* Teams
* Venue
* Live scores
* Scorecards
* Batting statistics
* Bowling statistics
* Partnerships

### 📊 Top Player Statistics

The application provides player performance analysis using batting and bowling statistics.

### 🗄️ SQL Analytics

The project uses a SQLite database containing cricket-related data.

The SQL Analytics section provides multiple analytical queries including:

* Indian players
* Recent matches
* Top ODI run scorers
* Large-capacity venues
* Team wins
* Players by role
* Highest scores by format
* Series analysis
* Match analytics

### ✏️ CRUD Operations

The application provides Create, Read, Update and Delete functionality for selected database records.

## 🔑 API Configuration

The application requires RapidAPI credentials.

For local development create:

```text
.streamlit/secrets.toml
```

with:

```toml
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY"
RAPIDAPI_HOST = "cricbuzz-cricket.p.rapidapi.com"
SCORECARD_API_URL = "YOUR_SCORECARD_API_URL"
```

**Do not commit `secrets.toml` to GitHub.**

The file is intentionally included in `.gitignore`.

## ▶️ Run Locally

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/Cricbuzz-LiveStats.git
```

Move into the project:

```bash
cd Cricbuzz-LiveStats
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your Streamlit secrets file:

```text
.streamlit/secrets.toml
```

Add your RapidAPI credentials and run:

```bash
streamlit run app.py
```

The application will normally open at:

```text
http://localhost:8501
```

## ☁️ Streamlit Cloud Deployment

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Sign in using GitHub.
4. Select **New app**.
5. Select the GitHub repository.
6. Select the main branch.
7. Set the main file to:

```text
app.py
```

8. Add the required secrets in the Streamlit Cloud Secrets section.
9. Deploy the application.

## 🔐 Secrets

Required secrets:

```toml
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY"
RAPIDAPI_HOST = "cricbuzz-cricket.p.rapidapi.com"
SCORECARD_API_URL = "YOUR_SCORECARD_API_URL"
```

Never commit API keys or other credentials to the repository.

## 📌 Important Note About SQLite

The project uses a local SQLite database:

```text
database/cricbuzz.db
```

The database file is included in the repository so that the deployed application can read the existing dataset.

SQLite is suitable for this project/demo deployment. However, persistent database writes on cloud deployments should be designed carefully because application environments can be recreated or reset.

## 👨‍💻 Author

Cricbuzz LiveStats Project
