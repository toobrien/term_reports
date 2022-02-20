from enum       import IntEnum
from json       import loads
from sqlite3    import connect
from time       import time
from typing     import List


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


def get_groups(
    symbol: str, 
    start:  str, 
    end:    str
) -> List:

    cur     = DB.cursor()
    groups  = []

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

        # no spot prices for this symbol, use m1 as approximation 
        
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

            spread_record = [ None ] * len(r)

            spread_record[r.id]     = ( 
                f"{group[j][r.month]}{group[j][r.id][-2:]}",
                f"{group[j + width][r.month]}{group[j + width][r.id][-2:]}",
            )
            spread_record[r.date]   = group[j][r.date]
            spread_record[r.dte]    = group[j][r.dte]
            spread_record[r.name]   = group[j][r.name]
            spread_record[r.month]  = (group[j][r.month], group[j + width][r.month])
            spread_record[r.year]   = (group[j][r.year], group[j + 1][r.year])
            spread_record[r.settle] = group[j + width][r.settle] - group[j][r.settle]
            spread_record[r.spot]   = group[j][r.spot]

            spread_group.append(spread_record)

    return spread_groups