# Severe Hail Predictor from NEXRAD Radar Data

This project aims to build a machine learning model to predict the probability and maximum size of hail produced by thunderstorms using NEXRAD Level 2 Doppler radar data.

## Project Overview

The goal is to leverage raw radar data (reflectivity, velocity) and ground truth storm reports to train a model that can identify which storm cells are likely to produce severe hail. This involves a full data science workflow, from raw data ingestion and processing to feature engineering, model training, and evaluation.

### Key Objectives
1.  **Data Ingestion:** Download NEXRAD radar scans and SPC storm reports for specific weather events.
2.  **Feature Engineering:** From the raw radar data, identify individual storm cells and calculate key predictive features like:
    * Vertically Integrated Liquid (VIL)
    * Maximum Expected Size of Hail (MESH)
    * Maximum Reflectivity (MAX_REF)
    * Echo Tops (ET)
3.  **Labeling:** Match the engineered features for each storm cell with ground truth hail reports from the SPC to create a labeled dataset.
4.  **Modeling:** Train classification (will it hail?) and regression (how large?) models on the final dataset.
5.  **Evaluation:** Assess the model's performance using appropriate metrics.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd severe-hail-predictor
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```