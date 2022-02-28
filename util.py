from enum                   import  IntEnum
from json                   import  loads
from sqlite3                import  connect
from typing                 import  List


DB_PATH = loads(open("./config.json").read())["db_path"]
DB      = connect(DB_PATH)


class r(IntEnum):

    id          = 0
    date        = 1
    name        = 2
    month       = 3
    year        = 4
    settle      = 5
    spot        = 6
    dte         = 7


class rs(IntEnum):

    id          = 0
    date        = 1
    name        = 2
    month       = 3
    year        = 4
    settle      = 5
    spot        = 6
    dte         = 7
    dte_back    = 8
    seq         = 9


def get_groups(
    symbol:     str, 
    start:      str,
    end:        str,
    use_spot:   bool
) -> List:

    cur     = DB.cursor()
    groups  = []
    rows    = []

    if use_spot:

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
                    INNER JOIN 
                        spot ON ohlc.name = spot.symbol AND ohlc.date = spot.date
                    INNER JOIN 
                        metadata ON ohlc.contract_id = metadata.contract_id
                WHERE
                    ohlc.name = "{symbol}" AND
                    ohlc.date BETWEEN "{start}" AND "{end}"
                ORDER BY 
                    ohlc.date ASC, ohlc.year ASC, ohlc.month ASC
                ;
            '''
        ).fetchall()

    if not rows:

        # either spot disabled, or no spot prices for this symbol,
        # use m1 as approximation 
        
        cur.row_factory = lambda cur, row: list(row)
        
        rows = cur.execute(
            f'''
                SELECT DISTINCT
                    ohlc.contract_id,
                    ohlc.date,
                    ohlc.name,
                    ohlc.month,
                    CAST(ohlc.year AS INT),
                    ohlc.settle,
                    NULL,
                    CAST(julianday(metadata.to_date) - julianday(ohlc.date) AS INT)
                FROM ohlc
                    INNER JOIN 
                        metadata ON ohlc.contract_id = metadata.contract_id
                WHERE
                    ohlc.name = "{symbol}" AND
                    ohlc.date BETWEEN "{start}" AND "{end}"
                ORDER BY 
                    ohlc.date ASC, ohlc.year ASC, ohlc.month ASC
                ;
            '''
        ).fetchall()

        groups = group_by_date(rows)

        for group in groups:

            for row in group:

                row[r.spot] = group[0][r.settle]

    else:

        # spot prices available, group records by date

        groups = group_by_date(rows)

    return groups


# strip negatives and 0 dte for log

def clean(groups: List):

    groups = [ 
        [ 
            row 
            for row in group
            if  row[r.dte]      > 0 and
                row[r.settle]   > 0 and
                row[r.spot]     > 0
        ]
        for group in groups
    ]

    groups = [
        group 
        for group in groups
        if group
    ]

    return groups


def group_by_date(rows: List):

    groups      = []
    cur_date    = rows[0][r.date]
    cur_set     = []

    for i in range(len(rows)):

        row_date = rows[i][r.date]

        if row_date != cur_date:

            groups.append(cur_set)
            cur_date = row_date
            cur_set  = [ rows[i] ]
        
        else:
            
            cur_set.append(rows[i])

    groups.append(cur_set)

    return groups


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
            spread_record[rs.date]      = group[j][r.date]
            spread_record[rs.dte]       = group[j][r.dte]
            spread_record[rs.dte_back]  = group[j + width][r.dte]
            spread_record[rs.name]      = group[j][r.name]
            spread_record[rs.month]     = (group[j][r.month], group[j + width][r.month])
            spread_record[rs.year]      = (group[j][r.year], group[j + 1][r.year])
            spread_record[rs.settle]    = group[j + width][r.settle] - group[j][r.settle]
            spread_record[rs.spot]      = group[j][r.spot]
            spread_record[rs.seq]       = j

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