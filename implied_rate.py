import  numpy                   as      np
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
import  polars                  as      pl
from    scipy.optimize          import  curve_fit
from    sys                     import  argv, path

path.append("..")

from    data.cat_df             import  cat_df


# python implied_rate.py HO 12 2023-08-01 2024-01-01


pl.Config.set_tbl_rows(50)
pl.Config.set_tbl_cols(25)


if __name__ == "__main__":

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
    time        = dtes / 365
    rates       = logs / time
    cal_logs    = logs[:, :-1] - logs[:, 1:]

    #print(dates)
    #print(m1_settles)
    #print(m1_dtes)
    #print(settles)
    #print(dtes)
    #print(logs)
    #print(dtes)
    #print(rates)

    fig = make_subplots(
            rows    = 2,
            cols    = 3, 
            specs   = [ 
                [ 
                    { "is_3d": True },
                    { "is_3d": True },
                    { "is_3d": True },
                
                ],
                [
                    { "is_3d": True },
                    { "is_3d": True },
                    { "is_3d": True }
                ]
            ],
            subplot_titles      = ( "logs", "logs_model", "errors", "rates", "cal_logs", "settles" ),
            horizontal_spacing  = 0.05,
            vertical_spacing    = 0.05
        )

    fig.add_trace(go.Surface(z = logs), 1, 1)
    fig.add_trace(go.Surface(z = rates), 2, 1)
    fig.add_trace(go.Surface(z = cal_logs), 2, 2)
    fig.add_trace(go.Surface(z = settles), 2, 3)

    # curve fit

    def f(x, a, c, d):

        return a * np.exp(-c * x) + d
    
    model = np.zeros(shape = logs.shape)

    for i in range(logs.shape[0]):

        popt, pcov = curve_fit(f, time[i], logs[i])

        model[i, :] = f(time[i], popt[0], popt[1], popt[2])

    errors = logs - model

    fig.add_trace(go.Surface(z = model, colorscale = "Viridis"), 1, 2)
    fig.add_trace(go.Surface(z = errors, colorscale = "viridis"), 1, 3)

    fig.show()

    pass