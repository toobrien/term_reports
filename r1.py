from    enum                    import  IntEnum
from    json                    import  loads
from    math                    import  log, sqrt
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    sqlite3                 import  connect
from    time                    import  time
from    typing                  import  List


config  = loads(open("./config.json").read())

DB_PATH     = config["db_path"]
START       = config["start"]
END         = config["end"]
MAX_DATES   = 500
MAX_MONTHS  = 12

class r(IntEnum):

    contract_id = 0
    date        = 1
    name        = 2
    month       = 3
    year        = 4
    settle      = 5
    spot        = 6
    dte         = 7


def load(
    symbol: str, 
    start:  str, 
    end:    str
) -> List:

    db = connect(DB_PATH)

    cur = db.cursor()

    rows = cur.execute(
        f'''
            SELECT DISTINCT
                ohlc.contract_id,
                ohlc.date,
                ohlc.name,
                ohlc.month,
                CAST(ohlc.year AS INT),
                ohlc.settle,
                spot.price,
                CAST(julianday(metadata.to_date) - julianday(ohlc.date) AS INT)
            FROM ohlc
                INNER JOIN spot ON ohlc.name = spot.symbol AND ohlc.date = spot.date
                INNER JOIN metadata ON ohlc.contract_id = metadata.contract_id
            WHERE
                ohlc.name = "{symbol}" AND
                ohlc.date BETWEEN "{start}" AND "{end}"
            ORDER BY ohlc.date ASC, ohlc.year ASC, ohlc.month ASC
            ;
        '''
    ).fetchall()

    db.close()

    return rows


def add_scatter(
    fig:    go.Figure,
    rows:   List
):

    # scatterplot

    dates       = sorted(
                    list(
                        set(
                            [ 
                                row[r.date] 
                                for row in rows 
                            ]
                        )
                    ),
                    reverse = True
                )[:MAX_DATES]
    latest      = rows[0][r.date]
    cur_opacity = 1.0
    step        = 0.8 / len(dates)
    opacities   = {}

    for date in dates:

        opacities[date] =  cur_opacity
        cur_opacity     -= step  

        trace_rows = [ 
            row 
            for row in rows 
            if row[r.date] == date
        ][:MAX_MONTHS]

        x = [ 
            row[r.dte]
            for row in trace_rows[:-1]
        ]

        y = [ 
            (trace_rows[i][r.settle] - trace_rows[i + 1][r.settle]) / trace_rows[i + 1][r.spot]
            for i in range(len(trace_rows) - 1)
        ]

        text = [ 
            f"{trace_rows[i][r.month]}{trace_rows[i][r.contract_id][-2:]}\n"
            f"{trace_rows[i + 1][r.month]}{trace_rows[i + 1][r.contract_id][-2:]}\n"
            f"{trace_rows[i][r.date]}" 
            for i in range(len(trace_rows) - 1)
        ]

        color = [ 
            "#FF0000" if row[r.date] == latest else "#0000FF" 
            for row in trace_rows
        ]

        opacity = [ 
            opacities[row[r.date]] 
            for row in trace_rows 
        ]

        fig.add_trace(
            go.Scatter(
                {
                    "x": x,
                    "y": y,
                    "text": text,
                    "name": date,
                    "mode": "markers",
                    "marker": {
                        "color": color,
                        "opacity": opacity
                    }
                }
            ),
            row = 1,
            col = 1
        )
    

def add_line(
    fig:    go.Figure, 
    rows:   List
):

    # group rows

    rows_by_date = {}

    for row in rows:

        date = row[r.date]

        if date not in rows_by_date:

            rows_by_date[date] = []

        rows_by_date[date].append(row)

    # calculate average discount
    
    x = []
    y = []

    for date, rows in rows_by_date.items():

        avg = 0

        for row in rows[:MAX_MONTHS]:

            avg += log(row[r.settle] / row[r.spot]) / (row[r.dte] / 365)

        avg /= min(MAX_MONTHS, len(rows))

        x.append(date)
        y.append(avg)

    # add trace

    fig.add_trace(
        go.Scatter(
            {
                "x":    x,
                "y":    y,
                "name": "average discount",
                "mode": "lines"
            }
        ),
        row = 2,
        col = 1
    )


if __name__ == "__main__":

    start_ts = time()

    # input

    symbol  = argv[1]
    start   = START if len(argv) < 3 else argv[2]
    end     = END   if len(argv) < 4 else argv[3]

    # get, sort, and and clean data

    rows = load(symbol, start, end)
    rows = [ 
        row
        for row in rows 
        if  row[r.dte]      > 0 and 
            row[r.settle]   > 0 and 
            row[r.spot]     > 0
    ]
    rows = sorted(rows, reverse = True, key = lambda row: row[r.date])

    # add plots and show

    fig = make_subplots(
        rows        = 2, 
        cols        = 1,
        row_heights = [ 0.7, 0.3 ] 
    )
    
    add_scatter(fig, rows)
    add_line(fig, rows)

    fig.show()

    # finished

    print(f"start date:\t{start}")
    print(f"end date:\t{end}")
    print(f"finished:\t{time() - start_ts: 0.1f}")