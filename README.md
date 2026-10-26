# Predicting Veterinary Demand Through Digital Epidemiology

**RMIT University | Master of Data Science | Capstone Project (P000292DS)**

**Industry Partner:** VetIQ (Curious Cat)  
**Academic Supervisor:** H. Ruda Nie  
**Project Team:** Asmi Faisel(s4134240), Bhairavi Chavan(s4133496), Sreelakshmi Thalodil Sunilkumar(s4146925)
**Year:** 2026

---

## Project Overview

This project explores how historical veterinary records, weather conditions, and Google search trends can be used to understand and forecast tick-related veterinary demand across South East Queensland (SEQ), Australia.

Working with VetIQ, we analysed consultation patterns, seasonal trends, temperature changes, and online search activity to investigate whether these external signals could help predict changes in veterinary demand.

The project focuses on short-term forecasting, particularly two-week-ahead predictions, to support better planning and resource allocation in veterinary clinics.

## Project Objectives

- Analyse historical veterinary appointment and consultation records.
- Identify seasonal and clinic-level patterns in tick-related consultations.
- Examine relationships between temperature, lagged weather conditions, and veterinary demand.
- Investigate whether Google search activity corresponds to changes in tick-related consultations.
- Develop and evaluate machine learning models for short-term demand forecasting.
- Compare models using historical information, weather data, and Google Trends.
- Develop an interactive dashboard to communicate the analysis and findings.

## Repository Structure

```text
P000292DS-Predicting-Veterinary-Demand-Through-Digital-Epidemiology/
│
├── Tick Analysis/
│   ├── Appointment.csv
│   ├── Clinics.csv
│   ├── Consultation.csv
│   └── Patients.csv
│
├── data/
│   ├── consultations_5year_part_001.csv
│   ├── consultations_5year_part_002.csv
│   ├── consultations_5year_part_003.csv
│   ├── consultations_5year_part_004.csv
│   ├── consultations_5year_part_005.csv
│   └── cleaned/
│
├── vetiq_dashboard/
│   ├── app.py
│   ├── static/
│   │   ├── style.css
│   │   └── js/
│   │       └── plotly.min.js
│   └── templates/
│       └── dashboard.html
│
├── 01_initial_dataset_analysis.ipynb
├── 02_updated_data_preprocessing.ipynb
├── 03_updated_dataset_analysis.ipynb
│
├── .gitattributes
├── .gitignore
└── README.md
```

The repository contains the analytical notebooks, supporting datasets, and Flask dashboard application. Some large datasets are divided into smaller files for Git LFS storage.

## Jupyter Notebooks

The Jupyter Notebooks document the project's analytical workflow, from initial data exploration through updated data preparation and analysis.

| Notebook | Purpose |
|---|---|
| `01_initial_dataset_analysis.ipynb` | Initial exploration of veterinary records, dataset structure, and consultation patterns. |
| `02_updated_data_preprocessing.ipynb` | Data cleaning, preprocessing, and preparation of updated datasets for analysis. |
| `03_updated_dataset_analysis.ipynb` | Analysis of the updated veterinary datasets, including trends and patterns relevant to demand forecasting. |

These notebooks provide a record of the data preparation and analytical work completed throughout the project.

## Data Sources

The project combines three main sources of information.

### Veterinary Clinical Data

Industry-provided datasets containing veterinary appointments, consultations, clinic information, patient records, reminders, and transactions.

### Weather Data

Historical weather information used to examine relationships between environmental conditions and veterinary consultation patterns, including potential lagged effects.

### Google Trends

Search interest data used to investigate whether online searches related to ticks correspond to changes in veterinary consultations.

## Data Preparation

The data preparation process included:

1. Reviewing dataset structures and identifying relevant fields.
2. Cleaning and standardising date and clinic information.
3. Identifying tick-related consultations.
4. Aggregating consultation activity into weekly and monthly time periods.
5. Aligning veterinary records with weather and Google Trends data.
6. Preparing modelling datasets and historical features.

The main forecasting analysis focused on eligible clinics across South East Queensland.

## Exploratory Data Analysis

Exploratory analysis was conducted to understand the relationships between veterinary demand and potential external indicators.

Key areas included:

- Weekly and monthly consultation trends.
- Seasonal patterns in tick-related consultations.
- Temperature and consultation activity.
- Lagged temperature relationships.
- Google search interest and consultation trends.
- Differences in consultation patterns across clinics.

The analysis helped identify patterns and informed the selection of features for forecasting models.

## Forecasting and Machine Learning

The project investigated several regression-based approaches, including:

- Linear Regression
- Ridge Regression
- Lasso Regression
- XGBoost

Ridge Regression was used for the main two-week-ahead forecasting comparisons because it supports regularisation and provides an interpretable framework for assessing different feature combinations.

### Forecasting Configurations

| Model | Input Features |
|---|---|
| R1 | Historical consultation activity and seasonality |
| R2 | Historical activity, seasonality, and temperature |
| R3 | Historical activity, seasonality, and Google Trends |
| R4 | Historical activity, seasonality, temperature, and Google Trends |

### Model Evaluation

Models were assessed using:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Persistence baseline comparisons
- Sensitivity analysis

Explanatory binomial models were also examined to investigate associations between tick-related consultations and external variables.

## Key Findings

The project identified seasonal patterns in tick-related veterinary consultations and explored their relationships with temperature and Google search interest.

However, incorporating external weather and search signals did not consistently improve forecasting accuracy beyond models using historical consultation activity and seasonality.

The findings demonstrate the importance of evaluating new predictive signals against established baselines before using them for operational planning.

## VetIQ Interactive Dashboard

The project includes a Flask-based dashboard designed to present analytical results and visualisations in an accessible format.

### Dashboard Components

- `app.py` — Flask application and backend logic.
- `templates/dashboard.html` — Dashboard interface.
- `static/style.css` — Dashboard styling.
- `static/js/plotly.min.js` — Plotly JavaScript library for interactive visualisations.

### Running the Dashboard

Install the Python packages required by the application, then navigate to the dashboard directory:

```bash
cd vetiq_dashboard
python app.py
```

Open the local address displayed by Flask in your browser.

**Note:** The dashboard may require additional data files and Python dependencies that are not included in this repository. Configure the relevant data paths before running the application.

## Git Large File Storage

Some datasets exceed GitHub's standard file-size limits and are managed using Git Large File Storage (Git LFS).

The five-year consultation dataset has been divided into five CSV parts. Each part includes a header and can be processed separately or combined in sequence.

To clone the repository with Git LFS:

```bash
git lfs install
git clone https://github.com/p000292dscuriouscat-wq/P000292DS-Predicting-Veterinary-Demand-Through-Digital-Epidemiology.git
cd P000292DS-Predicting-Veterinary-Demand-Through-Digital-Epidemiology
git lfs pull
```

## Data Confidentiality

The veterinary datasets were provided for an academic industry project. Access and reuse must comply with the industry partner's data-sharing and confidentiality requirements.

Clinical free-text and patient-related data may contain sensitive information and should only be accessed or distributed with appropriate authorisation.

## Project Outcome

This capstone project brought together veterinary clinical records, environmental information, Google Trends, statistical analysis, and machine learning to investigate opportunities for forecasting veterinary demand.

The results provide evidence about the usefulness and limitations of external signals for short-term forecasting and offer a foundation for further research and model development.

## Acknowledgements

We thank VetIQ (Curious Cat), our industry contact Mike Da Gama, academic supervisor H. Ruda Nie, and RMIT University for their guidance and support throughout the project.

---

**RMIT University — Master of Data Science Capstone Project, 2026**
