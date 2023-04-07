from bisect                 import bisect_left
from plotly.graph_objects   import Scatter
from plotly.subplots        import make_subplots
from requests               import get
from sys                    import argv


sym_to_idx = {
    "ZW":   "001602",
    "KE":   "001612",
    "ZC":   "002602",
    "ZO":   "004603",
    "ZS":   "005602",
    "ZL":   "007601",
    "ZM":   "026603",
    "ZR":   "039601",
    "HE":   "054642",
    "LE":   "057642",
    "CT":   "033661",
    "CC":   "073732",
    "SB":   "080732",
    "KC":   "083731",
    "ZT":   "042601",
    "ZF":   "044601",
    "ZN":   "043602",
    "TN":   "043607",
    "ZB":   "020601",
    "FF":   "045601",
    "S3":   "134741",
    "S1":   "134742",
    "NG":   "023651",
    "CL":   "067651",
    "RB":   "111659",
    "HO":   "022651",
    "VX":   "1170E1",
    "YM":   "12460+",
    "ES":   "13874+",
    "NQ":   "20974+",
    "RTY":  "239742",
    "NKD":  "240743",
    "SI":   "084691",
    "HG":   "085692",
    "GC":   "088691",
    "PA":   "075651",
    "PL":   "076691",
    "ALI":  "191651",
    "6R":   "089741",
    "6C":   "090741",
    "6S":   "092741",
    "6M":   "095741",
    "6B":   "096742",
    "6J":   "097741",
    "6E":   "099741",
    "6L":   "102741",
    "6Z":   "122741",
    "BTC":  "133741"
}


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

    for sym in symbols:
        
        index = sym_to_idx[sym]

        res = get(f"https://api.tvix.xyz/cot/contract/{index}").json()

        dates       = []
        comm_long   = []
        comm_short  = []
        comm_net    = []
        spec_long   = []
        spec_short  = []
        spec_net    = []
        non_long    = []
        non_short   = []
        non_net     = []
        oi          = []

        recs = reversed(res["records"].values())

        for rec in recs:

            dates.append(rec["date"])
            
            comm_long.append(int(rec["commercial_long_contracts"]))
            comm_short.append(int(rec["commercial_short_contracts"]))
            comm_net.append(comm_long[-1] - comm_short[-1])

            spec_long.append(int(rec["noncommercial_long_contracts"]))
            spec_short.append(int(rec["noncommercial_short_contracts"]))
            spec_net.append(spec_long[-1] - spec_short[-1])
            
            non_long.append(int(rec["nonreportable_long_contracts"]))
            non_short.append(int(rec["nonreportable_short_contracts"]))
            non_net.append(non_long[-1] - non_short[-1])

        j = bisect_left(dates, start) 
        k = bisect_left(dates, end)

        for trace_data in [
            ( comm_net, "#0000FF", "comm" ),
            ( spec_net, "#FF0000", "spec" ),
            ( non_net,  "#FFFF00", "non"  )
        ]:

            fig.add_trace(
                Scatter(
                    x       = dates[j:k],
                    y       = trace_data[0][j:k],
                    marker  = {
                        "color": trace_data[1]
                    },
                    name    = f"{sym} {trace_data[2]}"
                ),
                row = i,
                col = 1
            )

        i += 1

    fig.show()
            