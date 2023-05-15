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
    x           = [ pair[0] for pair in pairs ]
    y           = [ pair[1] for pair in pairs ]
    beta, alpha = linear_regression(x, y)

    up      = 0
    up_cont = 0
    dn      = 0
    dn_cont = 0

    for pair in pairs:

        if pair[0] > 0:
            
            up += 1
            
            if pair[1] > 0:

                up_cont += 1
        
        elif pair[0] < 0:

            dn += 1

            if pair[1] < 0:

                dn_cont += 1

    p_up_cont = up_cont / up
    p_dn_cont = dn_cont / dn

    print(f"beta:       \t{beta:0.2f}")
    print(f"alpha:      \t{alpha:0.2f}")
    print(f"samples:    \t{n_samples}")
    print(f"days:       \t{n_days}")
    print(f"p(move):    \t{p_move:0.2f}")
    print(f"p(up_cont): \t{p_up_cont:0.2f}\t{up_cont}/{up}")
    print(f"p(dn_cont): \t{p_dn_cont:0.2f}\t{dn_cont}/{dn}")

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