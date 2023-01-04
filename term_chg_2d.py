from    enum                    import  IntEnum
from    json                    import  loads
import  plotly.graph_objects    as      go
from    sys                     import  argv
from    util                    import  get_groups, r


config      = loads(open("./config.json").read())
START       = config["start"]
END         = config["end"]

def report(
    symbol:     str,
    days:       int,
    spread_len: int,
    max_terms:  int
):

    groups      = get_groups(symbol, START, END, False)[-days:]
    spreads     = {}
    outrights   = {}

    # outrights

    for group in groups:

        for rec in group[:max_terms]:

            id = rec[r.id].split("_")[1][-5:]
            id = id[0] + id[-2:]

            if id not in outrights:

                outrights[id] = []

            outrights[id].append(
                (
                    rec[r.date],
                    rec[r.settle]
                )
            )

    # spreads

    if spread_len > 0:

        for i in range(1, len(groups)):

            yesterday   = groups[i - 1]
            today       = groups[i]

            date = today[0][r.date]

            for j in range(spread_len, min(len(yesterday), len(today), max_terms), spread_len):

                m1_idx = j - spread_len
                m2_idx = j

                m1_rec_today        = today[m1_idx]
                m2_rec_today        = today[m2_idx]
                m1_rec_yesterday    = yesterday[m1_idx]
                m2_rec_yesterday    = yesterday[m2_idx]

                id      = f"{m1_rec_today[r.id][-5]}{m1_rec_today[r.id][-1]}-{m2_rec_today[r.id][-5]}{m2_rec_today[r.id][-1]}"
                settle  = m1_rec_today[r.settle] - m2_rec_today[r.settle]
                chg     = settle - (m1_rec_yesterday[r.settle] - m2_rec_yesterday[r.settle])
                text    = f"{id}<br>{date}<br>chg: {chg:0.4f}" 

                if id not in spreads:

                    spreads[id] = []

                spreads[id].append(
                    (
                        date,
                        settle,
                        text
                    )
                )

    fig = go.Figure()

    if spread_len == 0:

        for id, records in outrights.items():

            fig.add_trace(
                go.Scatter(
                    {
                        "x":    [ rec[0] for rec in records ],
                        "y":    [ rec[1] for rec in records ],     
                        "name": id
                    }
                )    
            )

    else:

        for id, records in spreads.items():

            fig.add_trace(
                go.Scatter(
                    {
                        "x":    [ rec[0] for rec in records ],
                        "y":    [ rec[1] for rec in records ],
                        "text": [ rec[2] for rec in records ],
                        "name": id
                    }
                )
            )

    fig.show()


if __name__ == "__main__":

    symbol      = argv[1]
    days        = int(argv[2])
    spread_len  = int(argv[3])
    max_terms   = int(argv[4])

    report(symbol, days, spread_len, max_terms)