import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  correlation
from    sys                     import  argv
from    typing                  import  List
from    util                    import  cot_rec, get_continuous, get_cot, r


COMM_COLOR = "#0000FF"
SPEC_COLOR = "#FF0000"
NON_COLOR  = "#FF00FF"


def get_stats(cot_recs: List, returns, field, window):

    val_by_date = {
        rec[cot_rec.date] : rec[field]
        for rec in cot_recs
    }

    oi_by_date = {
        rec[cot_rec.date] : rec[cot_rec.oi]
        for rec in cot_recs
    }

    chg_by_date = {
        cot_recs[i][cot_rec.date] : (cot_recs[i][field] - cot_recs[i - 1][field]) / abs(cot_recs[i - 1][field])
        for i in range(1, len(cot_recs))
    }

    ret_by_date = { ret[1] : ret[2] for ret in returns }

    zipped = [
        (date, ret_by_date[date], chg, val_by_date[date], oi_by_date[date])
        for date, chg in chg_by_date.items()
        if date in ret_by_date
    ]

    dates   = [ rec[0] for rec in zipped ]
    rets    = [ rec[1] for rec in zipped ]
    chgs    = [ rec[2] for rec in zipped ]
    vals    = [ rec[3] for rec in zipped ]
    ois     = [ rec[4] for rec in zipped ]

    # bad
    
    corrs = [
        correlation(rets[i - window:i], chgs[i - window:i])
        for i in range(window, len(dates))
    ]

    adj_vals = [ vals[i] / ois[i] for i in range(len(dates)) ]

    adj_rng = []
    max_adj = -1
    min_adj = 1

    for val in adj_vals:

        max_adj = max(val, max_adj)
        min_adj = min(val, min_adj)

        try:
        
            adj_rng.append((val - min_adj) / (max_adj - min_adj))

        except ZeroDivisionError:

            adj_rng.append(0)

    return ( dates, chgs, corrs, adj_vals, adj_rng )


if __name__ == "__main__":

    start   = argv[1]
    end     = argv[2]
    symbol  = argv[3]
    window  = int(argv[4])

    cot_recs    = get_cot(symbol, start, end)
    nearest     = get_continuous(symbol, start, end, 0, "nearest")
    returns     = get_continuous(symbol, start, end, 0, "returns")
    
    cum_rets    = []
    cur_ret     = 0
    init_date   = cot_recs[0][cot_rec.date]

    while returns[cur_ret][1] <= init_date:

        cur_ret += 1

    for i in range (1, len(cot_recs)):

        cur_cot     = cot_recs[i]
        prev_cot    = cot_recs[i - 1]
        cum_ret     = 0

        while returns[cur_ret][1] <= cur_cot[cot_rec.date]:

            ret_rec = returns[cur_ret]

            cum_ret += returns[cur_ret][2]
            cur_ret += 1
        
        cum_rets.append(cum_ret)

    dates   = [ rec[cot_rec.date] for rec in cot_recs[1:] ]
    prices  = [ 
            rec[r.settle] for rec in nearest
            if rec[r.date] in dates
        ]
    oi      = [ rec[cot_rec.oi] for rec in cot_recs[1:] ]

    comm_dates, comm_chgs, comm_corrs, comm_adj, comm_adj_rng = get_stats(cot_recs, returns, cot_rec.comm_net, window)
    spec_dates, spec_chgs, spec_corrs, spec_adj, spec_adj_rng = get_stats(cot_recs, returns, cot_rec.spec_net, window)

    fig = make_subplots(
            rows                = 5, 
            cols                = 1,
            shared_xaxes        = True,
            subplot_titles      = ( "price", "net", "adj", "adj_rng", "corrs" ),
            specs               = [ 
                                    [ {} ],
                                    [ { "secondary_y": True } ],
                                    [ {} ],
                                    [ {} ],
                                    [ {} ]
                                ],
            vertical_spacing    = 0.025
        )

    fig.add_trace(
        go.Scatter(
            {
                "x":    dates,
                "y":    prices,
                "name": "price"
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":            dates,
                "y":            [ rec[cot_rec.comm_net] for rec in cot_recs ],
                "marker":       { "color": COMM_COLOR },
                "name":         "comm_net"
            }
        ),
        row         = 2,
        col         = 1,
        secondary_y = False,
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":            dates,
                "y":            [ rec[cot_rec.spec_net] for rec in cot_recs ],
                "marker":       { "color": SPEC_COLOR },
                "name":         "spec_net"
            }
        ),
        row         = 2,
        col         = 1,
        secondary_y = False,
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":            dates,
                "y":            [ rec[cot_rec.non_net] for rec in cot_recs ],
                "marker":       { "color": NON_COLOR },
                "name":         "non_net"
            }
        ),
        row         = 2,
        col         = 1,
        secondary_y = False,
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":            dates,
                "y":            oi,
                "marker":       { "color": "#00FF00" },
                "name":         "oi"
            }
        ),
        row         = 2,
        col         = 1,
        secondary_y = True,
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":        comm_dates,
                "y":        comm_adj,
                "marker":   { "color": COMM_COLOR },
                "name":     f"comm_adj"
            }
        ),
        row = 3,
        col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":        spec_dates,
                "y":        spec_adj,
                "marker":   { "color": SPEC_COLOR },
                "name":     f"comm_adj"
            }
        ),
        row = 3,
        col = 1
    )
    fig.add_trace(
        go.Scatter(
            {
                "x":        comm_dates,
                "y":        comm_adj_rng,
                "marker":   { "color": COMM_COLOR },
                "name":     f"comm_adj_rng"
            }
        ),
        row = 4,
        col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":        spec_dates,
                "y":        spec_adj_rng,
                "marker":   { "color": SPEC_COLOR },
                "name":     f"comm_adj_rng"
            }
        ),
        row = 4,
        col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":        comm_dates[window:],
                "y":        comm_corrs,
                "marker":   { "color": COMM_COLOR },
                "name":     f"comm_corr[{window}]"
            }
        ),
        row = 5,
        col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":        spec_dates[window:],
                "y":        spec_corrs,
                "marker":   { "color": SPEC_COLOR },
                "name":     f"spec_corr[{window}]"
            }
        ),
        row = 5,
        col = 1
    )

    fig.show()