#!/bin/bash

# This script creates a new conda environment for the severe-hail-predictor project.

# Define the name of the environment
ENV_NAME="hail"

echo "--- Setting up the Conda environment for the Hail Predictor Project ---"

# Check if conda is installed
if ! command -v conda &> /dev/null
then
    echo "Conda could not be found."
    echo "Please install Miniconda or Anaconda and ensure it's in your PATH."
    exit 1
fi

# Create the conda environment with a specific Python version for reproducibility
echo ""
echo "Step 1: Creating the conda environment '$ENV_NAME' with Python 3.9..."
conda create --name $ENV_NAME python=3.9 -y

# Check if the environment was created successfully
if [ $? -ne 0 ]; then
    echo "Error: Failed to create the conda environment. Aborting."
    exit 1
fi

echo "Environment '$ENV_NAME' created successfully."
echo ""

# Install all the required packages into the new environment
# We specify the channel 'conda-forge' as it has the most up-to-date
# versions of many scientific Python packages.
echo "Step 2: Installing required packages from the 'conda-forge' channel..."
conda install --name $ENV_NAME --channel conda-forge \
    pandas \
    numpy \
    scikit-learn \
    boto3 \
    jupyter \
    matplotlib \
    seaborn \
    joblib \
    pyart-enigma \
    herbie-data \
    -y

if [ $? -ne 0 ]; then
    echo "Error: Failed to install packages. Please check your conda configuration."
    exit 1
fi

echo ""
echo "--- Setup Complete! ---"
echo ""
echo "To activate your new environment, run the following command:"
echo ""
echo "  conda activate $ENV_NAME"
echo ""

