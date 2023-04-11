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

    chg_by_date = {
        cot_recs[i][cot_rec.date] : (cot_recs[i][field] - cot_recs[i - 1][field]) / abs(cot_recs[i - 1][field])
        for i in range(1, len(cot_recs))
    }

    ret_by_date = { ret[1] : ret[2] for ret in returns }

    zipped = [
        (date, ret_by_date[date], chg, val_by_date[date])
        for date, chg in chg_by_date.items()
        if date in ret_by_date
    ]

    dates   = [ rec[0] for rec in zipped ]
    rets    = [ rec[1] for rec in zipped ]
    chgs    = [ rec[2] for rec in zipped ]
    vals    = [ rec[3] for rec in zipped ]

    corrs = [
        correlation(rets[i - window:i], chgs[i - window:i])
        for i in range(window, len(dates))
    ]

    pcts = [
        (vals[i] - min(vals[i - window:i + 1])) / 
        (max(vals[i - window:i + 1]) - min(vals[i - window:i + 1]))
        for i in range(window, len(dates))
    ]

    return ( dates, chgs, corrs, pcts )


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
    
    comm_dates, comm_chgs, comm_corrs, comm_pcts   = get_stats(cot_recs, returns, cot_rec.comm_net, window)
    spec_dates, spec_chgs, spec_corrs, spec_pcts   = get_stats(cot_recs, returns, cot_rec.spec_net, window)

    fig = make_subplots(
            rows = 4, 
            cols = 1,
            subplot_titles = ( "price", "net", "corr", "pct" )
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
                "x":    dates,
                "y":    [ rec[cot_rec.comm_net] for rec in cot_recs ],
                "marker": { "color": COMM_COLOR },
                "name": "comm_net"
            }
        ),
        row = 2, col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":    dates,
                "y":    [ rec[cot_rec.spec_net] for rec in cot_recs ],
                "marker": { "color": SPEC_COLOR },
                "name": "spec_net"
            }
        ),
        row = 2, col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":    dates,
                "y":    [ rec[cot_rec.non_net] for rec in cot_recs ],
                "marker": { "color": NON_COLOR },
                "name": "non_net"
            }
        ),
        row = 2, col = 1
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
        row = 3,
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
        row = 3,
        col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":        comm_dates[window:],
                "y":        comm_pcts,
                "marker":   { "color": COMM_COLOR },
                "name":     f"comm_pct[{window}]"
            }
        ),
        row = 4,
        col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":        spec_dates[window:],
                "y":        spec_pcts,
                "marker":   { "color": SPEC_COLOR },
                "name":     f"comm_pct[{window}]"
            }
        ),
        row = 4,
        col = 1
    )

    fig.show()