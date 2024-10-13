# Classic Stock Charts in Python


Create classic technical analysis stock charts in Python with minimal code.
The library is built around [matplotlib](https://github.com/matplotlib/matplotlib)
and [pandas](https://github.com/pandas-dev/pandas). 
Charts can be defined using a declarative interface,
based on a set of drawing primitives like `Candleststicks`, `Volume`
and technical indicators like `SMA`, `EMA`, `RSI`, `ROC`, `MACD`, etc ...


> **Warning**
> This project is experimental and the interface can change.
> For a similar project with a mature api you may want to look into
> [mplfinance](https://pypi.org/project/mplfinance/).


![Showcase Chart](/output/showcase.svg "Showcase")


## Typical Usage

```python
import yfinance as yf

from mplchart.chart import Chart
from mplchart.primitives import Candlesticks, Volume
from mplchart.indicators import ROC, SMA, EMA, RSI, MACD

ticker = 'AAPL'
prices = yf.Ticker(ticker).history('5y')

max_bars = 250

indicators = [
    Candlesticks(),
    Volume(),
    SMA(50),
    SMA(200),
    RSI(),
    MACD(),
]

chart = Chart(title=ticker, max_bars=max_bars)
chart.plot(prices, indicators)
chart.show()
```


## Conventions

Price data is expected to be presented as a pandas DataFrame
with columns `open`, `high`, `low`, `close` `volume`
and a timestamp index named `date` or `datetime`.
Please note, the library will automatically convert column
and index names to lower case for its internal use.


## Drawing Primitives

The library contains drawing primitives that can be used like an indicator in the plot api.
Primitives are classes and must be instantiated before being used as parameters to the plot api.

```python
from mplchart.chart import Chart
from mplchart.primitives import Candlesticks

indicators = [Candlesticks()]
chart = Chart(title=title, max_bars=max_bars)
chart.plot(prices, indicators)
```

The main drawing primitives are :
- `Candlesticks` for candlestick plots
- `OHLC` for open, high, low, close bar plots
- `Price` for price line plots
- `Volume` for volume bar plots
- `Peaks` to mark peaks and valleys


## Builtin Indicators

The libary contains some basic technical analysis indicators implemented in pandas/numpy.
Indicators are classes and must be instantiated before being used as parameters to the plot api.

Some of the indicators included are:

- `SMA` Simple Moving Average
- `EMA` Exponential Moving Average
- `WMA` Weighted Moving Average
- `HMA` Hull Moving Average
- `ROC` Rate of Change
- `RSI` Relative Strength Index
- `ATR` Average True Range
- `ATRP` Average True Range (Percent)
- `ADX` Average Directional Index
- `DMI` Directional Movement Index
- `MACD` Moving Average Convergence Divergence
- `PPO` Price Percentage Oscillator 
- `SLOPE` Slope (time linear regression)
- `BBANDS` Bollinger Bands



## Talib Abstract Functions

If you have [ta-lib](https://github.com/mrjbq7/ta-lib) installed you can use the library abstract functions as indicators.
The indicators are created by calling `Function` with the name of the indicator and its parameters.

```python
from mplchart.primitives import Candlesticks
from talib.abstract import Function

indicators = [
    Candlesticks(),
    Function('SMA', 50),
    Function('SMA', 200),
    Function('RSI'),
    Function('MACD'),
]
```


## Select target axes with `NewAxes` and `SameAxes` modifiers

Indicators usually plot in a new axes below, except for a few indicators that plot by default in the main axes. You can change the target axes to use for any indicator by using an axes modifier. A modifier is applied to an indicator with the `|` operator as in the example below.

```python
from mplchart.modifiers import NewAxes, SameAxes

indicators = [
    Candlesticks(),
    ROC(20) | NewAxes(),
    ROC(50) | SameAxes(),
]
```


## Custom Indicators

Any callable that accepts a prices dataframe and returns a series or dataframe can be used as an indicator.
You can also implement a custom indicator as a subclass of `Indicator`.

```python
from mplchart.model import Indicator
from mplchart.library import get_series, calc_ema

class DEMA(Indicator):
    """Double Exponential Moving Average"""

    same_scale = True
    # same_scale is an optional class attribute
    # to specify that the indicator can be drawn
    # on the same axes as the previous indicator

    def __init__(self, period: int = 20):
        self.period = period

    def __call__(self, prices):
        series = get_series(prices)
        ema1 = calc_ema(series, self.period)
        ema2 = calc_ema(ema1, self.period)
        return 2 * ema1 - ema2
```



## Examples

You can find example notebooks and scripts in the examples folder. 

## Installation

You can install the current version of this package with pip

```console
python -mpip install git+https://github.com/furechan/mplchart.git
```

## Dependencies

- python >= 3.9
- matplotlib
- pandas
- numpy


## Related Projects & Resources
- [stockcharts.com](https://stockcharts.com/) Classic stock charts and technical analysis reference
- [mplfinance](https://pypi.org/project/mplfinance/) Matplotlib utilities for the visualization, and visual analysis, of financial data
- [matplotlib](https://github.com/matplotlib/matplotlib) Matplotlib: plotting with Python
- [pandas](https://github.com/pandas-dev/pandas) Flexible and powerful data analysis / manipulation library for Python, providing labeled data structures similar to R data.frame objects, statistical functions, and much more
- [yfinance](https://github.com/ranaroussi/yfinance) Download market data from Yahoo! Finance's API
- [ta-lib](https://github.com/mrjbq7/ta-lib) Python wrapper for TA-Lib
