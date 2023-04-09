from plotly.graph_objects   import Bar, Scatter
from plotly.subplots        import make_subplots
from sys                    import argv
from util                   import get_continuous, get_cot


if __name__ == "__main__":

    start   = argv[1]
    end     = argv[2]
    symbol  = argv[3]

    cot_recs    = get_cot(symbol, start, end)
    ohlc        = get_continuous(symbol, start, end, 0, "nearest")
    rets        = get_continuous(symbol, start, end, 0, "returns")

    pass