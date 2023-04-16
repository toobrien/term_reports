from    math                    import  log
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  correlation
from    sys                     import  argv
from    typing                  import  List
from    util                    import  cot_rec, get_continuous, get_cot, r
from    v2.cot_v2_api           import  format, get_contract, report
from    v2.recs                 import  futs_only


PRICE_COLOR     = "#6495ED"
COMM_COLOR      = "#0000FF"
NONCOMM_COLOR   = "#FF0000"
NONREP_COLOR    = "#FF00FF"
OI_COLOR        = "#00FF00"


def get_stats(dates: List, net_pos: List, returns, window):

    n_recs = len(dates) 

    chg_by_date = {
        dates[i] : (net_pos[i] - net_pos[i - 1]) / abs(net_pos[i - 1])
        for i in range(1, n_recs)
    }

    ret_by_date = { ret[0] : ret[1] for ret in returns }

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


# example usage: python cot_detailed.py 2018-01-1 2024-01-01 NG 12

if __name__ == "__main__":

    start   = argv[1]
    end     = argv[2]
    symbol  = argv[3]
    window  = int(argv[4])

    cot_recs    = get_contract(report.futs_only, symbol, format.convenience, start, end)
    continuous  = get_continuous(symbol, start, end, 0, "spread_adjusted")
    dates       = cot_recs[futs_only.date]
    init_date   = dates[0]
    prices      = [ 
                    rec[r.settle] for rec in continuous
                    if rec[r.date] in dates
                ]

    # compute weekly returns

    settles = [ 
                ( 
                    rec[r.date],
                    rec[r.settle] 
                ) 
                for rec in continuous 
                if rec[r.date] in dates
            ]

    returns = [
        ( 
            settles[i][0],
            log(settles[i][1] / settles[i - 1][1])
        )
        for i in range(1, len(settles))
    ]

    comm_dates, comm_chgs, comm_corrs           = get_stats(cot_recs[futs_only.date], cot_recs[futs_only.comm_net], returns, window)
    noncomm_dates, noncomm_chgs, noncomm_corrs  = get_stats(cot_recs[futs_only.date], cot_recs[futs_only.noncomm_net], returns, window)

    fig = make_subplots(
            rows                = 4, 
            cols                = 1,
            shared_xaxes        = True,
            subplot_titles      = ( f"{symbol} price", "net", "net pct", "corrs" ),
            specs               = [ 
                                    [ {} ],
                                    [ { "secondary_y": True } ],
                                    [ {} ],
                                    [ {} ]
                                ],
            vertical_spacing    = 0.025
        )

    trace_params = [
        {
            "x":            [ rec[r.date] for rec in continuous ],
            "y":            [ rec[r.settle] for rec in continuous ],
            "name":         f"{symbol} (adjusted)",
            "marker":       { "color": PRICE_COLOR }, 
            "row":          1,
            "secondary_y":  False
        },
        {
            "x":            dates,
            "y":            cot_recs[futs_only.comm_net],
            "marker":       { "color": COMM_COLOR },
            "name":         "comm_net",
            "secondary_y":  True,
            "row":          2,
        },
        {
            "x":            dates,
            "y":            cot_recs[futs_only.noncomm_net],
            "marker":       { "color": NONCOMM_COLOR },
            "name":         "noncomm net",
            "row":          2,
            "secondary_y":  True
        }, 
        {
            "x":            dates,
            "y":            cot_recs[futs_only.nonrep_net],
            "marker":       { "color": NONREP_COLOR },
            "name":         "nonrep net",
            "row":          2,
            "secondary_y":  True
        },
        {
            "x":            dates,
            "y":            cot_recs[futs_only.oi],
            "marker":       { "color": OI_COLOR },
            "name":         "oi",
            "row":          2,
            "secondary_y":  False
        },
        {
            "x":            dates,
            "y":            cot_recs[futs_only.comm_net_pct],
            "marker":       { "color": COMM_COLOR },
            "name":         "comm net pct",
            "row":          3,
            "secondary_y":  False
        },
        {
            "x":            dates,
            "y":            cot_recs[futs_only.noncomm_net_pct],
            "marker":       { "color": NONCOMM_COLOR },
            "name":         "noncomm net pct",
            "row":          3,
            "secondary_y":  False
        },
        {
            "x":            dates[window:],
            "y":            comm_corrs,
            "marker":       { "color": COMM_COLOR },
            "name":         f"comm corr [{window}]",
            "row":          4,
            "secondary_y":  False
        },
        {
            "x":            dates[window:],
            "y":            noncomm_corrs,
            "marker":       { "color": NONCOMM_COLOR },
            "name":         f"noncomm corr [{window}]",
            "row":          4,
            "secondary_y":  False
        }
    ]

    for params in trace_params:

        fig.add_trace(
            go.Scatter(
                {
                    "x":        params["x"],
                    "y":        params["y"],
                    "marker":   params["marker"],
                    "name":     params["name"]
                }
            ),
            row         = params["row"],
            col         = 1,
            secondary_y = params["secondary_y"]
        )

    fig.show()