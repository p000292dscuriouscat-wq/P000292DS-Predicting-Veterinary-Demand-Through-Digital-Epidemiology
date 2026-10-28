# Predicting Veterinary Demand Through Digital Epidemiology

**RMIT University | Master of Data Science | Capstone Project (P000292DS)**

**Industry Partner:** Mike Da Gama, Founder, VetIQ (Curious Cat)  
**Academic Supervisor:** H. Ruda Nie  
**Project Team:** Asmi Faisel (s4134240), Bhairavi Chavan (s4133496), Sreelakshmi Thalodil Sunilkumar (s4146925)  
**Year:** 2026

---

## Project Overview

This project investigates how historical veterinary consultation records, weather conditions, and Google search trends can be used to understand and forecast tick-related veterinary demand across South East Queensland (SEQ), Australia.

Working with VetIQ (Curious Cat), the team analysed consultation patterns, seasonal variation, temperature conditions, and online search activity to evaluate whether external indicators could improve short-term veterinary demand forecasting.

The main forecasting task focused on **two-week-ahead predictions**, with the aim of supporting evidence-based planning and resource allocation in veterinary clinics.

## Project Objectives

- Analyse historical veterinary appointment and consultation records.
- Identify seasonal and clinic-level patterns in tick-related consultations.
- Examine relationships between temperature, lagged weather conditions, and veterinary demand.
- Investigate associations between Google search interest and tick-related consultations.
- Develop and evaluate statistical and machine learning models for short-term forecasting.
- Compare forecasting models using historical activity, seasonality, temperature, and Google Trends.
- Develop an interactive dashboard to communicate analytical findings.

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
├── silo_analysis.ipynb
│
├── .gitattributes
├── .gitignore
└── README.md
```

The repository contains the project's analytical notebooks, supporting datasets, and Flask dashboard application. Some large datasets are divided into smaller files and managed through Git Large File Storage (Git LFS).

## Jupyter Notebooks

The Jupyter Notebooks document the analytical workflow, from initial data exploration and preprocessing to forecasting and supplementary environmental analysis.

| Notebook | Purpose |
|---|---|
| `01_initial_dataset_analysis.ipynb` | Initial exploration of veterinary datasets, consultation records, data structures, and patterns. |
| `02_updated_data_preprocessing.ipynb` | Cleaning, standardisation, and preprocessing of updated veterinary consultation datasets. |
| `03_updated_dataset_analysis.ipynb` | Analysis of the expanded veterinary dataset, including consultation trends, seasonal patterns, and modelling investigations. |
| `silo_analysis.ipynb` | Supplementary SEQ weather analysis using SILO climate data, including weekly temperature aggregation, lagged temperature relationships, and forecasting experiments. |

The main temperature results presented in the final capstone report are based on **Open-Meteo weather data**. The SILO notebook documents additional exploratory and forecasting experiments conducted using a separate weather source.

These supplementary experiments provide additional context for assessing the contribution of environmental indicators, but should not be interpreted as a controlled comparison between Open-Meteo and SILO.

## Data Sources

The project integrates veterinary clinical records with external environmental and online search-interest data.

### 1. Veterinary Clinical Data

Industry-provided datasets include veterinary consultations, appointments, clinic information, patient records, reminders, and transactions.

The analysis focused on identifying tick-related consultations, examining clinic-level variation, and preparing aggregated consultation counts and rates for statistical analysis and forecasting.

Clinical records were cleaned and standardised to address issues such as inconsistent identifiers, duplicate representations of consultation events, and incomplete coding.

### 2. Weather Data

Two historical weather sources were investigated.

**Open-Meteo Historical Weather API**

Open-Meteo provided historical temperature observations used in the main analysis and reported forecasting experiments.

Temperature records were matched to clinic locations and aggregated into weekly indicators to investigate contemporaneous and lagged relationships with tick-related consultation demand.

**SILO Climate Database**

SILO climate data were used for supplementary weather analysis across South East Queensland.

The supplementary workflow included examining historical temperature records, preparing weekly weather indicators, exploring temperature–consultation relationships, and evaluating temperature-based forecasting configurations.

This work is documented separately in `silo_analysis.ipynb`.

The SILO experiments were exploratory and are not presented as a direct, controlled comparison of the two weather data sources.

### 3. Google Trends

Google Trends data were collected to investigate whether online search activity related to ticks could provide additional information about veterinary consultation demand.

Search terms were organised into three keyword baskets:

- Tick-related symptoms and conditions.
- Tick treatment and prevention.
- Tick prevention products.

The keyword datasets were consolidated using their common monthly periods and prepared for alignment with veterinary consultation records.

Google Trends values represent normalised relative search interest rather than absolute search volumes. The Queensland-wide geographic coverage also differs from the SEQ-focused clinic analysis.

## Data Preparation

The data preparation workflow included:

1. Reviewing veterinary dataset structures and identifying relevant fields.
2. Cleaning and standardising consultation dates, clinic identifiers, and other variables.
3. Identifying tick-related consultation records.
4. Checking potential duplicate events and inconsistencies.
5. Aggregating consultation activity into weekly and monthly periods.
6. Preparing clinic-level consultation rates using appropriate denominators.
7. Matching weather observations to relevant clinic locations.
8. Aligning external indicators with consultation data.
9. Generating historical, seasonal, and lagged features for modelling.

The main forecasting analysis focused on eligible veterinary clinics across South East Queensland.

## Exploratory Data Analysis

Exploratory analysis investigated historical consultation patterns and their relationships with potential external indicators.

Key areas included:

- Weekly and monthly tick-related consultation trends.
- Seasonal patterns and historical variation.
- Differences in consultation activity across clinics.
- Temperature and tick-related consultation relationships.
- One-week and two-week lagged temperature associations.
- Google Trends search-interest patterns.
- Potential relationships between external indicators and consultation demand.

The exploratory findings informed feature selection, modelling decisions, and interpretation of forecasting results.

## Statistical Analysis and Forecasting

The project combined explanatory statistical modelling with predictive machine learning experiments.

### Explanatory Modelling

Binomial Generalised Linear Models (GLMs) were examined to investigate associations between tick-related consultations and external indicators.

The explanatory configurations included:

| Model | Variables |
|---|---|
| M1 | Clinic effects and seasonality |
| M2 | Clinic effects, seasonality, and temperature |
| M3 | Clinic effects, seasonality, and Google Trends |
| M4 | Clinic effects, seasonality, temperature, and Google Trends |

Model fit was examined using the Akaike Information Criterion (AIC).

These models were used to investigate explanatory relationships rather than to establish causal effects.

### Predictive Modelling

Several forecasting approaches were investigated, including:

- Linear Regression
- Ridge Regression
- Lasso Regression
- Random Forest
- XGBoost
- SARIMA

Ridge Regression was used for the principal two-week-ahead forecasting comparisons because it provided a regularised and interpretable framework for assessing the incremental contribution of external predictors.

### Ridge Forecasting Configurations

| Model | Input Features |
|---|---|
| R1 | Historical consultation activity and seasonality |
| R2 | Historical consultation activity, seasonality, and temperature |
| R3 | Historical consultation activity, seasonality, and Google Trends |
| R4 | Historical consultation activity, seasonality, temperature, and Google Trends |

The configurations were designed to test whether temperature and Google search-interest indicators improved predictive performance beyond historical consultation patterns and seasonal information.

### Model Evaluation

Forecasting performance was assessed using:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Persistence baseline comparisons
- Chronological training and testing
- Sensitivity analysis

The project also explored monthly regional-count modelling and seasonal forecasting approaches as supplementary investigations.

## Supplementary SILO Weather Analysis

In addition to the principal Open-Meteo-based analysis, the project investigated SILO historical weather data in a separate analytical workflow.

The supplementary SEQ analysis involved:

- Preparing historical and recent SILO weather observations.
- Examining temporal coverage and missing temperature values.
- Selecting relevant weather locations for the SEQ study area.
- Aggregating daily weather observations into weekly indicators.
- Aligning weekly temperature records with veterinary consultation activity.
- Examining contemporaneous and lagged temperature associations.
- Comparing baseline and temperature-enhanced forecasting configurations.

The supplementary forecasting visualisations indicated that adding temperature produced predictions closely resembling those of the baseline model.

These observations were exploratory and should not be interpreted as proof that the two weather sources perform equivalently. Differences in model configuration, data preparation, or evaluation periods may affect comparisons.

The supporting analysis is available in `silo_analysis.ipynb`.

## Key Findings

The project identified seasonal patterns and substantial clinic-level variation in tick-related veterinary consultations.

Temperature showed some positive lagged associations with consultation activity, but these relationships were generally weak.

Google Trends data provided additional contextual information about public search interest but did not consistently demonstrate reliable leading predictive value.

Across the main forecasting comparisons, incorporating temperature and Google Trends did not consistently improve accuracy beyond models using historical consultation activity and seasonality.

The findings highlight the importance of evaluating external predictive signals against established baselines before incorporating them into operational forecasting systems.

## VetIQ Interactive Dashboard

A Flask-based dashboard was developed to communicate the project's analytical results through an interactive interface.

The dashboard was designed to support exploration of historical consultation patterns, seasonal variation, external indicators, and forecasting outputs.

### Dashboard Components

- `app.py` — Flask application and backend logic.
- `templates/dashboard.html` — Dashboard interface.
- `static/style.css` — Dashboard styling.
- `static/js/plotly.min.js` — Plotly JavaScript library for interactive visualisations.

### Running the Dashboard

Install the required Python packages and navigate to the dashboard directory:

```bash
cd vetiq_dashboard
python app.py
```

Open the local address displayed by Flask in your browser.

**Note:** The dashboard may require additional data files and Python dependencies that are not included in this repository. Configure the required data paths and dependencies before running the application.

The dashboard is a research prototype rather than a validated operational early-warning system.

## Git Large File Storage

Some datasets exceed GitHub's standard file-size limits and are managed using Git Large File Storage (Git LFS).

The five-year consultation dataset has been divided into five CSV files. Each file includes a header and can be processed separately or combined in sequence.

To clone the repository with Git LFS:

```bash
git lfs install
git clone https://github.com/p000292dscuriouscat-wq/P000292DS-Predicting-Veterinary-Demand-Through-Digital-Epidemiology.git
cd P000292DS-Predicting-Veterinary-Demand-Through-Digital-Epidemiology
git lfs pull
```

## Data Confidentiality

The veterinary datasets were provided for an academic industry project. Access and reuse must comply with the industry partner's data-sharing and confidentiality requirements.

Clinical free-text, patient-related information, and other potentially sensitive data should only be accessed or distributed with appropriate authorisation.

The presence of files in a repository does not imply permission for unrestricted reuse or redistribution.

## Project Outcome

This capstone project integrated veterinary clinical records, environmental information, Google Trends, statistical analysis, and machine learning to investigate opportunities for forecasting tick-related veterinary demand.

The main results demonstrated that external temperature and search-interest indicators did not consistently provide additional forecasting accuracy beyond historical consultation activity and seasonality.

The supplementary SILO analysis extended the environmental investigations and provided further exploratory evidence about temperature-based forecasting.

Together, the analytical workflow and interactive dashboard provide a foundation for future research, model refinement, and stakeholder evaluation.

## Acknowledgements

We thank VetIQ (Curious Cat), our industry contact Mike Da Gama, academic supervisor H. Ruda Nie, and RMIT University for their guidance and support throughout the project.

