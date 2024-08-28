# ChartWise
This is a simple Flask-based web application that allows users to track stocks and monitor their performance based on various technical indicators, including RSI, moving averages, MACD, and Bollinger Bands.

![image](https://github.com/user-attachments/assets/ae2d0314-8351-4d9f-8796-9a178cf37b41)


## Features

- **Track multiple stocks** by adding the stock symbol and your suggested purchase price.
- **View real-time stock data**, including current price, gain/loss percentage, and various technical indicators.
- **Sortable columns** to organize your data efficiently.

## Installation

To run this application locally, follow these steps:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/sidhu2690/ChartWise.git
    cd ChartWise
    ```



2. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the application:**

    ```bash
    python app.py
    ```

4. **Open your web browser** and go to `http://127.0.0.1:5000/` to access the app.

## Usage

- **Add Stock:** Enter the stock symbol (e.g., `AAPL` for Apple Inc.) and your suggested price in the provided fields and click "Add Stock" to start tracking.
- **View Stock Data:** The app will fetch real-time data and display it in a table, including current price, gain/loss percentage, and technical indicators.
- **Sort Columns:** Click on the column headers to sort the data based on that specific column.

## Technical Indicators Included

- **RSI (Relative Strength Index):** Measures the magnitude of recent price changes to evaluate overbought or oversold conditions.
- **Moving Averages (Short & Long):** Shows the average price over a specified number of days to smooth out price data.
- **MACD (Moving Average Convergence Divergence):** A trend-following momentum indicator that shows the relationship between two moving averages of a stock's price.
- **Bollinger Bands:** Consists of a middle band being a simple moving average, and an upper and a lower band at a distance defined by standard deviations.

## License

This project is licensed under the MIT License.

## Contributions

Contributions are welcome! Please open an issue or submit a pull request on GitHub if you would like to contribute to the project.

---

**Happy Coding!** 🎉
