from    math                    import  log
import  plotly.graph_objects    as      go
from    statistics              import  linear_regression
from    sys                     import  argv
from    util                    import  get_continuous, r


# usage: python move.py ZR 1 3.0

def report(
    symbol: str,
    term:   int, 
    thresh: float
):

    con = get_continuous(symbol, None, None, term, "spread_adjusted")

    ret     = [ 
                    log(con[i][r.settle] / con[i - 1][r.settle]) * 100
                    for i in range(1, len(con))
                ]
    pairs   = []

    for i in range(len(ret) - 1):

        if abs(ret[i]) >= thresh:

            pairs.append(( ret[i], ret[i + 1] ))

    n_samples   = len(pairs)
    n_days      = len(con)
    p_move      = n_samples / (n_days - 2)
    x = [ pair[0] for pair in pairs ]
    y = [ pair[1] for pair in pairs ]

    beta, alpha = linear_regression(x, y)

    print(f"beta:       {beta:0.2f}")
    print(f"alpha:      {alpha:0.2f}")
    print(f"samples:    {n_samples}")
    print(f"days:       {n_days}")
    print(f"p(move):    {p_move:0.2f}")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            {
                "x":    x,
                "y":    y,
                "name": "ret",
                "mode": "markers"
            }
        )
    )
    
    fig.show()


if __name__ == "__main__":

    symbol  = argv[1]
    term    = int(argv[2])
    thresh  = float(argv[3])

    report(symbol, term, thresh)