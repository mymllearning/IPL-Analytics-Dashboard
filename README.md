# 🏏 IPL Analytics Dashboard

Welcome to the **IPL Analytics Dashboard**! This interactive web application provides a comprehensive analysis of Indian Premier League (IPL) matches from 2008 to 2024. Built with [Streamlit](https://streamlit.io/), it offers dynamic visualizations and detailed insights into teams, players, venues, and match outcomes.

## 🚀 Features

*   **🏆 Match Analysis**: Explore match statistics per season, team win records, toss decision impacts, and match result types (chasing vs. defending).
*   **🧑 Player Analysis**: Discover top run-scorers and wicket-takers. Dive deep into individual player statistics with run distributions and performance metrics.
*   **📍 Venue Analysis**: Analyze match trends across different stadiums, including high-scoring venues and average first innings scores.
*   **⏱️ Over Analysis**: Visualize run rates and standard wicket fall patterns across overs.
*   **📊 Heatmaps**: View head-to-head win matrices between teams to understand rivalries.
*   **🎨 Interactive UI**: A clean, dark-themed interface powered by Streamlit and Plotly for an engaging user experience.

## 🛠️ Tech Stack

*   **Python**: Core programming language.
*   **Streamlit**: For building the web application interface.
*   **Pandas**: For data manipulation and processing.
*   **Plotly & Seaborn/Matplotlib**: For interactive and static data visualizations.
*   **NumPy**: For numerical computations.

## 📂 Project Structure

```
ipl-analytics-dashboard/
├── app.py                # Main Streamlit application file
├── requirements.txt      # List of Python dependencies
├── .gitignore            # Git ignore file
├── data/                 # Directory containing dataset files
│   ├── matches.csv       # Match-level data
│   └── deliveries.csv    # Ball-by-ball delivery data
└── README.md             # Project documentation
```

## ⚙️ Installation & Setup

Follow these steps to set up the project locally:

1.  **Clone the Repository** (if applicable) or navigate to the project directory:
    ```bash
    cd /path/to/ipl\ data\ set
    ```

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Prepare Data**:
    Ensure you have the IPL datasets placed in the `data/` directory.
    *   `data/matches.csv`
    *   `data/deliveries.csv`

## 🏃 Usage

Run the Streamlit application using the following command:

```bash
streamlit run app.py
```

Comparison and insights will appear in your default web browser at `http://localhost:8501`.

## 📊 Dataset

The dashboard uses IPL data covering seasons from 2008 to 2024.
*   **Matches**: Contains details like season, city, date, team1, team2, toss winner, toss decision, result, etc.
*   **Deliveries**: Detailed ball-by-ball data for every match.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the dashboard.
