# Anomaly Detection in Time Series Data 📈🔍

This project focuses on detecting anomalies in **patient heartbeat data** using a **Recurrent Autoencoder** model. The goal is to identify abnormal heartbeats (anomalies) in ECG time series data. 🩺📊

---

## Table of Contents 📑
1. [Overview](#overview-)
2. [Installation](#installation-)
3. [Usage](#usage-)
4. [Code Structure](#code-structure-)
5. [Results](#results-)
6. [License](#license-)

---

## Overview 🚀

This project:
- Uses a **Recurrent Autoencoder** to model normal ECG time series data. 🤖📈
- Detects anomalies by comparing reconstruction errors with a predefined threshold. 🚨📉
- Visualizes training/validation loss and anomaly detection results. 📊📉

---

## Installation 🛠️

To run this project, you need to install the required libraries. Run the following commands:

```bash
!pip install pandas liac-arff
!pip install torch
!pip install seaborn matplotlib
```

---

## Usage 🖥️

1. **Download Dataset**: The script downloads the ECG5000 dataset containing heartbeat data.
2. **Preprocess Data**: The dataset is split into normal and anomalous samples.
3. **Train Autoencoder**: A Recurrent Autoencoder is trained on normal ECG data.
4. **Detect Anomalies**: The model detects anomalies by comparing reconstruction errors to a threshold.
5. **Visualize Results**: Training/validation loss and anomaly detection results are visualized.

---

## Code Structure 🗂️

- **Data Collection**:
  - Downloads and preprocesses the ECG5000 dataset.
  - Splits the data into normal and anomalous samples.

- **Model Training**:
  - Defines and trains a Recurrent Autoencoder on normal ECG data.
  - Saves the trained model for future use.

- **Anomaly Detection**:
  - Uses the trained model to detect anomalies in the test dataset.
  - Visualizes the distribution of reconstruction errors.

- **Visualization**:
  - Plots training and validation loss over epochs.
  - Displays histograms of reconstruction errors for normal and anomalous data.

---

## Results 📊

- **Training/Validation Loss**: The model achieves low reconstruction errors on normal data.
- **Anomaly Detection**: The model identifies anomalies by comparing reconstruction errors to a threshold.
- **Visualization**: Histograms and plots provide insights into the model's performance.

---

## License 📜

This project is licensed under the **MIT License**. Feel free to use, modify, and distribute it as needed.

---

## Example Output 🖼️

Here’s an example of the model detecting anomalies in ECG data:

```plaintext
Number of correct predictions: X/Y
```

---

## Dependencies 📦

- `pandas`
- `liac-arff`
- `torch`
- `seaborn`
- `matplotlib`

---

## Author 👨‍💻

This project was created by **[Navid Falah](https://github.com/navidfalah)**. Feel free to reach out for questions or collaborations at **navid.falah7@gmail.com**! 🤝
