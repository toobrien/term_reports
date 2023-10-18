import  numpy                   as      np
import  plotly.graph_objects    as  go
import  polars                  as      pl
from    sys                     import  argv, path
from    time                    import  time

path.append("..")

from    data.cat_df             import  cat_df


# python implied_rate.py HO 12 2023-08-01 2024-01-01


pl.Config.set_tbl_rows(50)
pl.Config.set_tbl_cols(25)


if __name__ == "__main__":

    t0      = time()
    symbol  = argv[1]
    months  = int(argv[2])
    start   = argv[3]
    end     = argv[4]

    df = cat_df(
        "futs", 
        symbol, 
        start, 
        end
    ).sort(
        [ "date", "year", "month" ]
    ).select(
        [
            "contract_id",
            "date",
            "settle",
            "dte"
        ]
    )

    contracts   = df.filter(df["date"] == df["date"][-1])["contract_id"]
    contracts   = list(contracts[0:months])
    df          = df.filter(df["contract_id"].is_in(contracts))
    
    settles     = df.pivot(index = "date", columns = "contract_id", values = "settle", aggregate_function = "first")

    #print(settles)

    dtes        = df.pivot(index = "date", columns = "contract_id", values = "dte", aggregate_function = "first")
    
    dates       = settles.select("date")
    m1_settles  = settles[contracts[0]]
    m1_dtes     = dtes[contracts[0]]

    settles     = settles.drop( ["date", contracts[0] ])
    dtes        = dtes.drop([ "date", contracts[0] ])

    dates       = np.array(dates)
    m1_settles  = np.tile(np.array(m1_settles), ( settles.shape[1], 1 )).T
    m1_dtes     = np.tile(np.array(m1_dtes), ( dtes.shape[1], 1 )).T
    settles     = settles.to_numpy()
    dtes        = dtes.to_numpy()

    logs        = np.log(settles / m1_settles)
    dtes        = dtes - m1_dtes
    rates       = logs / (dtes / 365)

    #print(dates)
    #print(m1_settles)
    #print(m1_dtes)
    #print(settles)
    #print(dtes)
    #print(logs)
    #print(dtes)
    #print(rates)

    fig = go.Figure(data = go.Surface(z = rates))

    fig.show()

    pass