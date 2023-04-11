import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  correlation
from    sys                     import  argv
from    typing                  import  List
from    util                    import  cot_rec, get_continuous, get_cot, r


def get_stats(cot_recs: List, returns, field, window):

    chg_by_date = {
        cot_recs[i][cot_rec.date] : (cot_recs[i][field] - cot_recs[i - 1][field]) / abs(cot_recs[i - 1][field])
        for i in range(1, len(cot_recs))
    }

    ret_by_date = { ret[1] : ret[2] for ret in returns }

    zipped = [
        (date, ret_by_date[date], chg)
        for date, chg in chg_by_date.items()
        if date in ret_by_date
    ]

    dates   = [ rec[0] for rec in zipped ]
    rets    = [ rec[1] for rec in zipped ]
    chgs    = [ rec[2] for rec in zipped ]

    corrs = [
        correlation(rets[i - window:i], chgs[i - window:i])
        for i in range(window, len(dates))
    ]

    return ( dates, chgs, corrs )


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
    
    comm_dates, comm_chgs, comm_corrs   = get_stats(cot_recs, returns, cot_rec.comm_net, window)
    spec_dates, spec_chgs, spec_corrs   = get_stats(cot_recs, returns, cot_rec.spec_net, window)

    fig = make_subplots(rows = 3, cols = 1)

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

    '''
    fig.add_trace(
        go.Bar(
            {
                "x":    dates,
                "y":    cum_rets,
                "name": "returns"
            }
        ),
        row = 2,
        col = 1
    )

    fig.add_trace(
        go.Bar(
            {
                "x":    comm_dates,
                "y":    comm_chgs,
                "name": "comm_chgs"
            }
        ),
        row = 2,
        col = 1
    )

    fig.add_trace(
        go.Bar(
            {
                "x":    spec_dates,
                "y":    spec_chgs,
                "name": "spec_chgs"
            }
        ),
        row = 2,
        col = 1
    )
    '''

    fig.add_trace(
        go.Scatter(
            {
                "x":    dates,
                "y":    [ rec[cot_rec.comm_net] for rec in cot_recs ],
                "marker": { "color": "#0000FF" },
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
                "marker": { "color": "#FF0000" },
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
                "marker": { "color": "#FF00FF" },
                "name": "non_net"
            }
        ),
        row = 2, col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":    comm_dates[window:],
                "y":    comm_corrs,
                "name": f"comm_corr[{window}]"
            }
        ),
        row = 3,
        col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":    spec_dates[window:],
                "y":    spec_corrs,
                "name": f"spec_corr[{window}]"
            }
        ),
        row = 3,
        col = 1
    )

    fig.show()

    pass