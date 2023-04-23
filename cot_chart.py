from plotly.graph_objects   import Scatter
from plotly.subplots        import make_subplots
from sys                    import argv
from v2.cot_v2_api          import format, get_contract, report
from v2.recs                import futs_only


# usage: python cot_chart.py 2018-01-01 2024-01-01 CL [ ... ] RB


if __name__ == "__main__":

    start       = argv[1]
    end         = argv[2]
    symbols     = argv[3:]

    fig = make_subplots(
        rows            = len(symbols),
        cols            = 1,
        subplot_titles  = tuple(symbols)
    )

    # fig.update_layout(barmode = "overlay")

    i = 1

    for symbol in symbols:
        
        con = get_contract(report.futs_only, symbol, format.convenience, start, end)

        for trace_data in [
            ( con[futs_only.comm_net_pct],      "#0000FF", "comm net pct"       ),
            ( con[futs_only.noncomm_net_pct],   "#FF0000", "noncomm net pct"    ),
            ( con[futs_only.nonrep_net_pct],    "#FFFF00", "nonrep net pct"     )
        ]:

            fig.add_trace(
                Scatter(
                    x       = con[futs_only.date],
                    y       = trace_data[0],
                    marker  = {
                        "color": trace_data[1]
                    },
                    name    = f"{symbol} {trace_data[2]}"
                ),
                row = i,
                col = 1
            )

        i += 1

    fig.show()
            