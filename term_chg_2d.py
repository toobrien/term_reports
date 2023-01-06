from    copy                    import  deepcopy
from    json                    import  loads
from    numpy                   import  corrcoef
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
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

        today = group

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

    # format correlation matrix

    series_length   = 0
    corr_source     = deepcopy(spreads) if spread_len != 0 else deepcopy(outrights)
    todays_date     = today[0][r.date]
    
    for id, records in corr_source.items():

        series_length = max(series_length, len(records))

    to_delete = [ 
                    id for id, records in corr_source.items()
                    if records[-1][0] != todays_date
                ]

    for id in to_delete:

        # don't care about expired spreads

        del corr_source[id]

    # normalize series length for correlation calculation

    for id, records in corr_source.items():

        pad_length      = series_length - len(records)
        initial_value   = records[0][1]
        corr_source[id] = [ ( None, initial_value, None ) ] * pad_length + records

    # compute todays and yesterdays correlations

    corr_labels         = [ id for id, _ in corr_source.items() ]
    corr_settles        = [ 
                            [ record[1] for record in records ]
                            for _, records in corr_source.items()
                        ]
    corr_returns        = [
                            [
                                settles[i] / settles[i - 1] - 1 if settles[i - 1] != 0 else 0
                                for i in range(1, len(settles))
                            ]
                            for settles in corr_settles
                        ]
    # yesterdays_returns  = [ returns[:-1] for returns in corr_returns ]

    todays_correlations     = corrcoef(corr_returns).tolist()

    # not used
    
    # yesterdays_correlations = corrcoef(yesterdays_returns).tolist()

    matrix_dim = len(corr_labels)

    # calculate direction divergences and color cells accordingly

    direction   = [ [ 0 ] * matrix_dim for i in range(matrix_dim) ]
    cell_colors = [ [ None ] * matrix_dim for i in range(matrix_dim) ]

    for i in range(matrix_dim):

        for j in range(matrix_dim):

            # sign = todays_correlations[i][j] - yesterdays_correlations[i][j]

            sign = corr_returns[i][-1] * corr_returns[j][-1]

            cell_colors[i][j] = "white" if sign >= 0 else "red"

            # format correlations as text

            todays_correlations[i][j] = f"{todays_correlations[i][j]: 0.3f}"

    # expand matrices for row headers

    for i in range(matrix_dim):

        cell_colors[i].insert(0, "white" if corr_returns[i][-1] >= 0 else "red")
    
    for i in range(0, matrix_dim):

        todays_correlations[i].insert(0, corr_labels[i])

    # transpose because... plotly. copied from stack overflow.

    todays_correlations = list(map(list, zip(*todays_correlations)))
    cell_colors = list(map(list, zip(*cell_colors)))

    # generate settlement charts

    fig = make_subplots(
        rows    = 2,
        cols    = 1,
        specs   = [
                    [ { "type": "scatter" } ],
                    [ { "type": "table" } ]
                ],
        subplot_titles = [ symbol, None ]
    )

    if spread_len == 0:

        for id, records in outrights.items():

            fig.add_trace(
                go.Scatter(
                    {
                        "x":    [ rec[0] for rec in records ],
                        "y":    [ rec[1] for rec in records ],     
                        "name": id
                    }
                ),
                row = 1,
                col = 1
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
                ),
                row = 1,
                col = 1
            )

    # generate correlation table

    fig.add_trace(
        go.Table(
            header = {
                "values": [""] + corr_labels,
                "fill_color": "gray"
            },
            cells = {
                "values": todays_correlations,
                "fill_color": cell_colors
            }
        ),
        row = 2,
        col = 1
    )

    fig.show()



if __name__ == "__main__":

    symbol      = argv[1]
    days        = int(argv[2])
    spread_len  = int(argv[3])
    max_terms   = int(argv[4])

    report(symbol, days, spread_len, max_terms)