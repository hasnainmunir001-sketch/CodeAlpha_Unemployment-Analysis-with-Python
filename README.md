# 📊 Unemployment in India — Analysis & Interactive Dashboard

An end-to-end data analysis project on unemployment trends in India, with a special
focus on the impact of **COVID-19**, built with **Python** and deployed as an
interactive **Streamlit** web app.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

🔗 **Live demo:** _add your Streamlit Cloud link here after deployment_

---

## 📌 Project Overview

This project analyzes state-wise unemployment rate data for India and answers:

- How did **COVID-19** affect unemployment rates across the country?
- Are there **seasonal patterns** in unemployment (monthly / yearly cycles)?
- Which **regions / states** and **rural vs. urban areas** were hit hardest?
- What **policy directions** can be derived from the observed trends?

The final deliverable is a fully interactive dashboard where a user can upload
their own CSV (in the same schema) or explore a bundled sample dataset.

---

## ✨ Features

- **Data cleaning pipeline** — handles missing values, stray whitespace in column
  names, date parsing, and duplicate removal (`utils/data_processing.py`)
- **CSV upload** — analyze your own unemployment dataset directly in the browser
- **Interactive filters** — filter by region, area (rural/urban), and date range
- **Trend visualizations** — time series, top/bottom regions, rural vs. urban comparison, correlation heatmap
- **COVID-19 impact analysis** — pre- vs. post-lockdown comparison with a clear cut-off marker (25 March 2020)
- **Seasonality analysis** — month-wise and year-wise averages, box plots
- **Auto-generated insights** — plain-language takeaways and suggested policy directions
- **Downloadable output** — export the filtered/cleaned dataset as CSV

---

## 🗂️ Project Structure

```
unemployment-analysis-india/
├── app.py                     # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation (this file)
├── .gitignore
├── data/
│   └── sample_unemployment_data.csv   # Bundled sample dataset
├── utils/
│   └── data_processing.py      # Cleaning & feature-engineering functions
└── assets/                     # Screenshots / images for README (optional)
```

---

## 📥 Dataset

This project is designed around the **Unemployment in India** dataset on Kaggle:

🔗 https://www.kaggle.com/datasets/gokulrajkmv/unemployment-in-india

Expected columns (the app also tolerates minor spacing/naming differences):

| Column | Description |
|---|---|
| `Region` | State / region name |
| `Date` | Observation date (monthly) |
| `Frequency` | Reporting frequency (Monthly) |
| `Estimated Unemployment Rate (%)` | % of unemployed people |
| `Estimated Employed` | Number of people employed |
| `Estimated Labour Participation Rate (%)` | % of working-age population in the labour force |
| `Area` | Rural / Urban |

### Using the real dataset

```python
import kagglehub

path = kagglehub.dataset_download("gokulrajkmv/unemployment-in-india")
print("Path to dataset files:", path)
```

Download the CSV from the path above, then upload it directly in the app's
sidebar — no code changes required.

---

## 🚀 Getting Started (Local Setup)

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/unemployment-analysis-india.git
cd unemployment-analysis-india
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push this project to a **public GitHub repository** (steps below).
2. Go to **https://share.streamlit.io** and sign in with GitHub.
3. Click **"New app"** → select your repository, branch (`main`), and set
   **Main file path** to `app.py`.
4. Click **Deploy**. Streamlit Cloud will automatically install everything
   listed in `requirements.txt`.
5. Once deployed, copy the live app URL and paste it at the top of this
   README under **Live demo**.

---

## 🧭 Step-by-Step: Uploading This Project to GitHub

```bash
# 1. Initialize git inside the project folder
cd unemployment-analysis-india
git init

# 2. Add all files
git add .

# 3. Commit
git commit -m "Initial commit: Unemployment in India analysis dashboard"

# 4. Create a new repository on GitHub (via the website), then link it
git branch -M main
git remote add origin https://github.com/<your-username>/unemployment-analysis-india.git

# 5. Push
git push -u origin main
```

> Replace `<your-username>` with your actual GitHub username, and create the
> empty repository on github.com first (do **not** initialize it with a
> README there, to avoid merge conflicts).

---

## 🔍 Key Insights (Example Findings)

- Unemployment rates spiked sharply around **April–May 2020**, coinciding with
  India's nationwide COVID-19 lockdown, before gradually recovering over the
  following months.
- **Rural** and **urban** areas responded differently to the shock, with
  urban unemployment often reacting faster but rural areas showing slower
  recovery in some states.
- Certain states consistently show **above-average** unemployment rates,
  suggesting a need for targeted state-level employment programs.
- Mild **seasonal fluctuations** are visible across months, useful for
  planning seasonal public-works or credit-support programs.

*(Exact figures depend on the dataset used — see the in-app "Insights" tab
for numbers computed from your uploaded data.)*

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Pandas / NumPy** — data cleaning & manipulation
- **Matplotlib / Seaborn** — statistical visualizations
- **Plotly Express** — interactive charts
- **Streamlit** — web app framework & deployment

---

## 📄 License

This project is released under the [MIT License](LICENSE). Feel free to fork,
modify, and use it for learning or portfolio purposes.

---

## 🙋 About

Built as a portfolio / academic project demonstrating data cleaning,
exploratory data analysis, and dashboard deployment skills using Python and
Streamlit.
