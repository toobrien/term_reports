from            bisect                  import  bisect_left
from            datetime                import  datetime
from            enum                    import  IntEnum
from            json                    import  loads
from            math                    import  log
import          plotly.graph_objects    as      go
import          polars                  as      pl
from            requests                import  get
from            statistics              import  correlation, StatisticsError
from            typing                  import  List

BEGIN       = "1900-01-01"
END         = "2100-01-01"
DB_PATH     = loads(open("./config.json").read())["db_path"]
DB          = pl.read_parquet(DB_PATH)
GROUP_CACHE = {}


class r(IntEnum):

    id              = 0
    date            = 1
    name            = 2
    month           = 3
    year            = 4
    settle          = 5
    spot            = 6
    dte             = 7
    discount_rate   = 8


class rs(IntEnum):

    id          = 0
    date        = 1
    name        = 2
    month       = 3
    year        = 4
    settle      = 5
    settle_pct  = 6
    spot        = 7
    dte         = 8
    dte_back    = 9
    seq         = 10


def get_groups(
    symbol:     str, 
    start:      str = None,
    end:        str = None
) -> List:

    key = (symbol, start, end)

    if key in GROUP_CACHE:

        return GROUP_CACHE[key]

    if not start:

        start = BEGIN

    if not end:

        end = END

    filtered = DB.filter(
                                (pl.col("name") == symbol) &
                                (pl.col("date") >= start)   & 
                                (pl.col("date") < end)
                            ).sort(
                                [ "date", "year", "month" ]
                            )
    
    rows = filtered.select(
                            [
                                "contract_id",
                                "date",
                                "name",
                                "month",
                                "year",
                                "settle",
                                "dte"
                            ]
                        ).rows()
    groups      = []
    cur_date    = rows[0][1]
    spot        = rows[0][5] # use front month price as "spot"... hack
    cur_group   = []

    for row in rows:

        if row[r.date] != cur_date:

            # new day

            # compute discount
            
            for rec in cur_group:

                rec[r.discount_rate] =  log(rec[r.settle] / spot) / (rec[r.dte] / 365) \
                                        if rec[r.settle] > 0 and spot > 0 and rec[r.dte] > 0 else 0

            # add group to output and set next group's date, spot
            
            groups.append(cur_group)

            cur_date    = row[1]
            spot        = row[5]
            cur_group   = []
        
        rec = [
            row[0],         # id
            row[1],         # date
            row[2],         # name (symbol)
            row[3],         # month
            int(row[4]),    # year
            row[5],         # settle
            spot,           # "spot" (M1 price)
            row[6],         # dte
            None            # discount rate
        ]

        cur_group.append(rec)
    
    # compute discount for final group; append final group

    for rec in cur_group:

                rec[r.discount_rate] =  log(rec[r.settle] / spot) / (rec[r.dte] / 365) \
                                        if rec[r.settle] > 0 and spot > 0 and rec[r.dte] > 0 else 0

    groups.append(cur_group)

    GROUP_CACHE[key] = groups

    return groups


# returns a continuous contract of ohlcv for each of "term"

def get_continuous(
    symbol: str,
    start:  str,
    end:    str,
    term:   int,
    mode:   str
):

    groups  = get_groups(symbol, start, end, False)
    series  = []

    if mode == "nearest":

        # schwager pg. 280

        series = [ group[term] for group in groups ]

    elif mode == "spread_adjusted":

        # schwager pg. 282; use ratio instead of difference

        cum_adj = 1.0

        for i in range(1, len(groups)):

            try:

                cur         = groups[i][term]
                prev        = groups[i - 1][term]
                prev_next   = groups[i - 1][term + 1]

                if cur[r.id] != prev[r.id]:

                    # contract expired yesterday, compute roll factor

                    cum_adj *= prev_next[r.settle] / prev[r.settle]

                rec             = [ field for field in cur ]
                rec[r.settle]   *= cum_adj

                series.append(rec)
                
            except Exception as e:

                # negative price or missing a term

                print(e)
        
        for rec in series:

            rec[r.settle] /= cum_adj

    return series


def spreads(groups: List, width: int):

    spread_groups = [ [] for _ in groups ]

    for i in range(len(groups)):

        group           = groups[i]
        spread_group    = spread_groups[i] 

        for j in range(len(group) - width):

            spread_record = [ None ] * len(rs)

            spread_record[rs.id]     = ( 
                f"{group[j][rs.month]}{group[j][rs.id][-2:]}",
                f"{group[j + width][rs.month]}{group[j + width][rs.id][-2:]}",
            )
            
            spread_record[rs.date]          =   group[j][r.date]
            spread_record[rs.dte]           =   group[j][r.dte]
            spread_record[rs.dte_back]      =   group[j + width][r.dte]
            spread_record[rs.name]          =   group[j][r.name]
            spread_record[rs.month]         =   (group[j][r.month], group[j + width][r.month])
            spread_record[rs.year]          =   (group[j][r.year], group[j + 1][r.year])
            spread_record[rs.settle]        =   group[j + width][r.settle] - group[j][r.settle]
            spread_record[rs.spot]          =   group[j][r.spot]
            spread_record[rs.settle_pct]    =   spread_record[rs.settle] / spread_record[rs.spot] \
                                                if spread_record[rs.spot] != 0 else 0
            spread_record[rs.seq]           =   j

            spread_group.append(spread_record)

    return spread_groups


def by_season(spread_groups: List):

    season_groups = {}

    for day in spread_groups:

        for row in day:

            months = row[rs.month]

            if months not in season_groups:

                season_groups[months] = []

            season_groups[months].append(row)

    return season_groups


def by_date(spread_groups: List):

    day_groups = {
        day[0][rs.date]: day
        for day in spread_groups
        if len(day) > 0
    }

    return day_groups


def by_year(spread_records: List):

    year_groups = {}

    for record in spread_records:

        if record[rs.year] not in year_groups:

            year_groups[record[rs.year]] = []

        year_groups[record[rs.year]].append(record)

    return year_groups


class cor_r(IntEnum):

    date        = 0
    dte         = 1
    correlation = 2


def spot_correlation(rows: List, length: int):

    diff_spot   = [ None ]
    diff_settle = [ None ]

    for i in range(1, len(rows)):

        x = rows[i][rs.spot] - rows[i - 1][rs.spot]
        y = rows[i][rs.settle] - rows[i - 1][rs.settle]

        diff_spot.append(x)
        diff_settle.append(y)

    res = [ 
        [ row[rs.date], row[rs.dte], None ]
        for row in rows 
    ]

    for i in range(length + 1, len(rows)):

        try:

            res[i][cor_r.correlation] = correlation(
                diff_spot[i - length:i],
                diff_settle[i - length:i]
            )

        except StatisticsError:

            res[i][cor_r.correlation] = None

    return res


class avg_r(IntEnum):

    date        = 0
    year        = 1
    day_of_year = 2
    avg_settle  = 3


def term_avg_by_year(
    spread_groups:  List,
    start:          int,
    end:            int,
    mode:           str
):

    avgs = []

    # calculate average spread for each day

    for i in range(len(spread_groups)):

        group = spread_groups[i][start:end]

        if group:

            year = group[0][rs.date][0:4]
            avg  = 0

            for row in group:

                if mode == "abs":
                
                    avg += row[rs.settle]
                
                elif mode == "pct":

                    avg += row[rs.settle] / row[rs.spot]

            avg /= len(group)

            avgs.append(
                [ 
                    group[0][rs.date],
                    group[0][rs.date][0:4],
                    datetime.strptime(group[0][rs.date], "%Y-%m-%d").timetuple().tm_yday,
                    avg
                ]
            )

    # group averages by year

    by_year = {}

    for row in avgs:

        year = row[1]

        if year not in by_year:

            by_year[year] = []

        by_year[year].append(row)

    return by_year


def add_trace(
    fig:        go.Figure,
    rows:       List,
    id:         str,
    ax_x:       int,
    ax_y:       int,
    ax_text:    int,
    fig_row:    int,
    fig_col:    int,
    mode:       str = "markers",
    color:      str = None
):

    x       = [ r[ax_x] for r in rows ]
    y       = [ r[ax_y] for r in rows ]
    text    = [ r[ax_text] for r in rows ]

    fig.add_trace(
        go.Scattergl(
            {
                "x": x,
                "y": y,
                "text": text,
                "name": id,
                "mode": mode,
                "marker_color": color
            }
        ),
        row = fig_row,
        col = fig_col
    )


# Commitment of Traders

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


class cot_rec(IntEnum):

    date        = 0
    comm_long   = 1
    comm_short  = 2
    comm_net    = 3
    spec_long   = 4
    spec_short  = 5
    spec_net    = 6
    non_long    = 7
    non_short   = 8
    non_net     = 9
    oi          = 10

def get_cot(symbol, start, end):

    index = sym_to_idx[symbol]

    res = get(f"https://api.tvix.xyz/cot/contract/{index}").json()

    dates   = list(reversed(res["records"].keys()))
    i       = bisect_left(dates, start) 
    j       = bisect_left(dates, end)
    recs    = list(reversed(res["records"].values()))[i:j]

    cot_recs = [
        (
            rec["date"],
            int(rec["commercial_long_contracts"]),
            int(rec["commercial_short_contracts"]),
            int(rec["commercial_long_contracts"]) - int(rec["commercial_short_contracts"]),
            int(rec["noncommercial_long_contracts"]),
            int(rec["noncommercial_short_contracts"]),
            int(rec["noncommercial_long_contracts"]) - int(rec["noncommercial_short_contracts"]),
            int(rec["nonreportable_long_contracts"]),
            int(rec["nonreportable_short_contracts"]),
            int(rec["nonreportable_long_contracts"]) - int(rec["nonreportable_short_contracts"]),
            int(rec["open_interest"])
        )
        for rec in recs
    ]

    return cot_recs


