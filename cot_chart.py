from plotly.graph_objects   import Scatter
from plotly.subplots        import make_subplots
from sys                    import argv
from util                   import cot_rec, get_cot

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
        
        cot_recs = get_cot(symbol, start, end)

        dates       = [ r[cot_rec.date]     for r in cot_recs ]
        comm_net    = [ r[cot_rec.comm_net] for r in cot_recs ]
        spec_net    = [ r[cot_rec.spec_net] for r in cot_recs ]
        non_net     = [ r[cot_rec.non_net]  for r in cot_recs ]

        for trace_data in [
            ( comm_net, "#0000FF", "comm" ),
            ( spec_net, "#FF0000", "spec" ),
            ( non_net,  "#FFFF00", "non"  )
        ]:

            fig.add_trace(
                Scatter(
                    x       = dates,
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
            