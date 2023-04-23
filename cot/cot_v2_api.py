from bisect             import bisect_left
from v2.common_symbols  import COMMON_SYMBOLS
from enum               import IntEnum
from v2.raw_recs        import *
from requests           import get
from v2.recs            import *


class report(IntEnum):

    disagg_futs_only        = 0
    disagg_futs_and_opts    = 1
    fin_futs_only           = 2
    fin_futs_and_opts       = 3
    futs_only               = 4
    futs_and_opts           = 5
    cit_supp                = 6


class format(IntEnum):

    none        = 0
    raw         = 1
    convenience = 2


API_ROOT    = "https://tvix.xyz/cot_v2"
REPORT_STR  = {
                report.disagg_futs_only:        "disagg_futs_only",
                report.disagg_futs_and_opts:    "disagg_futs_and_opts",
                report.fin_futs_only:           "fin_futs_only",
                report.fin_futs_and_opts:       "fin_futs_and_opts",
                report.futs_only:               "futs_only",
                report.futs_and_opts:           "futs_and_opts",
                report.cit_supp:                "cit_supp"
            }
DATE_KEY    = 2


def convenience_recs(report_type: int, data: dict):

    conv = {}

    if report_type in [ report.disagg_futs_only, report.disagg_futs_and_opts ]:

        n_recs = len(data[disagg_futs_only_raw.report_date_as_yyyy_mm_dd])

        conv[disagg_futs_only.date]                 = [ x           for x in data[disagg_futs_only_raw.report_date_as_yyyy_mm_dd]                                               ]
        conv[disagg_futs_only.prod_merc_long]       = [ int(x)      for x in data[disagg_futs_only_raw.prod_merc_positions_long_all]                                            ]
        conv[disagg_futs_only.prod_merc_long_pct]   = [ float(x)    for x in data[disagg_futs_only_raw.pct_of_oi_prod_merc_long_all]                                            ]
        conv[disagg_futs_only.prod_merc_short]      = [ int(x)      for x in data[disagg_futs_only_raw.prod_merc_positions_short_all]                                           ]
        conv[disagg_futs_only.prod_merc_short_pct]  = [ float(x)    for x in data[disagg_futs_only_raw.pct_of_oi_prod_merc_short_all]                                           ]
        conv[disagg_futs_only.prod_merc_net]        = [ conv[disagg_futs_only.prod_merc_long][i]        - conv[disagg_futs_only.prod_merc_short][i]     for i in range(n_recs)  ]
        conv[disagg_futs_only.prod_merc_net_pct]    = [ conv[disagg_futs_only.prod_merc_long_pct][i]    - conv[disagg_futs_only.prod_merc_short_pct][i] for i in range(n_recs)  ]
        conv[disagg_futs_only.swap_long]            = [ int(x)      for x in data[disagg_futs_only_raw.swap_positions_long_all]                                                 ]
        conv[disagg_futs_only.swap_long_pct]        = [ float(x)    for x in data[disagg_futs_only_raw.pct_of_oi_swap_long_all]                                                 ]
        conv[disagg_futs_only.swap_short]           = [ int(x)      for x in data[disagg_futs_only_raw.swap__positions_short_all]                                               ]
        conv[disagg_futs_only.swap_short_pct]       = [ float(x)    for x in data[disagg_futs_only_raw.pct_of_oi_swap_short_all]                                                ]
        conv[disagg_futs_only.swap_spread]          = [ int(x)      for x in data[disagg_futs_only_raw.swap__positions_spread_all]                                              ]
        conv[disagg_futs_only.swap_spread_pct]      = [ float(x)    for x in data[disagg_futs_only_raw.pct_of_oi_swap_spread_all]                                               ]
        conv[disagg_futs_only.swap_net]             = [ conv[disagg_futs_only.swap_long][i]     - conv[disagg_futs_only.swap_short][i]      for i in range(n_recs)              ]
        conv[disagg_futs_only.swap_net_pct]         = [ conv[disagg_futs_only.swap_long_pct][i] - conv[disagg_futs_only.swap_short_pct][i]  for i in range(n_recs)              ]
        conv[disagg_futs_only.managed_long]         = [ int(x)      for x in data[disagg_futs_only_raw.m_money_positions_long_all]                                              ]
        conv[disagg_futs_only.managed_long_pct]     = [ float(x)    for x in data[disagg_futs_only_raw.pct_of_oi_m_money_long_all]                                              ]
        conv[disagg_futs_only.managed_short]        = [ int(x)      for x in data[disagg_futs_only_raw.m_money_positions_short_all]                                             ]
        conv[disagg_futs_only.managed_short_pct]    = [ float(x)    for x in data[disagg_futs_only_raw.pct_of_oi_m_money_short_all]                                             ]
        conv[disagg_futs_only.managed_spread]       = [ int(x)      for x in data[disagg_futs_only_raw.m_money_positions_spread_all]                                            ]
        conv[disagg_futs_only.managed_spread_pct]   = [ float(x)    for x in data[disagg_futs_only_raw.pct_of_oi_m_money_spread_all]                                            ]
        conv[disagg_futs_only.managed_net]          = [ conv[disagg_futs_only.managed_long][i]      - conv[disagg_futs_only.managed_short][i]       for i in range(n_recs)      ]
        conv[disagg_futs_only.managed_net_pct]      = [ conv[disagg_futs_only.managed_long_pct][i]  - conv[disagg_futs_only.managed_short_pct][i]   for i in range(n_recs)      ]
        conv[disagg_futs_only.other_long]           = [ int(x)      for x in data[disagg_futs_only_raw.other_rept_positions_long_all]                                           ]
        conv[disagg_futs_only.other_long_pct]       = [ float(x)    for x in data[disagg_futs_only_raw.pct_of_oi_other_rept_long_all]                                           ]
        conv[disagg_futs_only.other_short]          = [ int(x)      for x in data[disagg_futs_only_raw.other_rept_positions_short_all]                                          ]
        conv[disagg_futs_only.other_short_pct]      = [ float(x)    for x in data[disagg_futs_only_raw.pct_of_oi_other_rept_short_all]                                          ]
        conv[disagg_futs_only.other_spread]         = [ int(x)      for x in data[disagg_futs_only_raw.other_rept_positions_spread_all]                                         ]
        conv[disagg_futs_only.other_spread_pct]     = [ float(x)    for x in data[disagg_futs_only_raw.pct_of_oi_other_rept_spread_all]                                         ]
        conv[disagg_futs_only.other_net]            = [ conv[disagg_futs_only.other_long][i]        - conv[disagg_futs_only.other_short][i]     for i in range(n_recs)          ]
        conv[disagg_futs_only.other_net_pct]        = [ conv[disagg_futs_only.other_long_pct][i]    - conv[disagg_futs_only.other_short_pct][i] for i in range(n_recs)          ]
        conv[disagg_futs_only.nonrep_long]          = [ int(x)      for x in data[disagg_futs_only_raw.nonrept_positions_long_all]                                              ]
        conv[disagg_futs_only.nonrep_long_pct]      = [ float(x)    for x in data[disagg_futs_only_raw.pct_of_oi_nonrept_long_all]                                              ]
        conv[disagg_futs_only.nonrep_short]         = [ int(x)      for x in data[disagg_futs_only_raw.nonrept_positions_short_all]                                             ]
        conv[disagg_futs_only.nonrep_short_pct]     = [ float(x)    for x in data[disagg_futs_only_raw.pct_of_oi_nonrept_short_all]                                             ]
        conv[disagg_futs_only.nonrep_net]           = [ conv[disagg_futs_only.nonrep_long][i]       - conv[disagg_futs_only.nonrep_short][i]        for i in range(n_recs)      ]
        conv[disagg_futs_only.nonrep_net_pct]       = [ conv[disagg_futs_only.nonrep_long_pct][i]   - conv[disagg_futs_only.nonrep_short_pct][i]    for i in range(n_recs)      ]
        conv[disagg_futs_only.oi]                   = [ int(x)      for x in data[disagg_futs_only_raw.open_interest_all]                                                       ]

    elif report_type in [ report.fin_futs_only, report.fin_futs_and_opts ]:

        n_recs = len(data[fin_futs_only_raw.report_date_as_yyyy_mm_dd])

        conv[fin_futs_only.date]                    = [ x           for x in data[fin_futs_only_raw.report_date_as_yyyy_mm_dd]                                              ]
        conv[fin_futs_only.dealer_long]             = [ int(x)      for x in data[fin_futs_only_raw.dealer_positions_long_all]                                              ]
        conv[fin_futs_only.dealer_long_pct]         = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_dealer_long_all]                                              ]
        conv[fin_futs_only.dealer_short]            = [ int(x)      for x in data[fin_futs_only_raw.dealer_positions_short_all]                                             ]
        conv[fin_futs_only.dealer_short_pct]        = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_dealer_short_all]                                             ]
        conv[fin_futs_only.dealer_spread]           = [ int(x)      for x in data[fin_futs_only_raw.dealer_positions_spread_all]                                            ]
        conv[fin_futs_only.dealer_spread_pct]       = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_dealer_spread_all]                                            ]
        conv[fin_futs_only.dealer_net]              = [ conv[fin_futs_only.dealer_long][i]      - conv[fin_futs_only.dealer_short][i]       for i in range(n_recs)          ]
        conv[fin_futs_only.dealer_net_pct]          = [ conv[fin_futs_only.dealer_long_pct][i]  - conv[fin_futs_only.dealer_short_pct][i]   for i in range(n_recs)          ]
        conv[fin_futs_only.asset_mgr_long]          = [ int(x)      for x in data[fin_futs_only_raw.asset_mgr_positions_long_all]                                           ]
        conv[fin_futs_only.asset_mgr_long_pct]      = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_asset_mgr_long_all]                                           ]
        conv[fin_futs_only.asset_mgr_short]         = [ int(x)      for x in data[fin_futs_only_raw.asset_mgr_positions_short_all]                                          ]
        conv[fin_futs_only.asset_mgr_short_pct]     = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_asset_mgr_short_all]                                          ]
        conv[fin_futs_only.asset_mgr_spread]        = [ int(x)      for x in data[fin_futs_only_raw.asset_mgr_positions_spread_all]                                         ]
        conv[fin_futs_only.asset_mgr_spread_pct]    = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_asset_mgr_spread_all]                                         ]
        conv[fin_futs_only.asset_mgr_net]           = [ conv[fin_futs_only.asset_mgr_long][i]       - conv[fin_futs_only.asset_mgr_short][i]        for i in range(n_recs)  ]
        conv[fin_futs_only.asset_mgr_net_pct]       = [ conv[fin_futs_only.asset_mgr_long_pct][i]   - conv[fin_futs_only.asset_mgr_short_pct][i]    for i in range(n_recs)  ]
        conv[fin_futs_only.leveraged_long]          = [ int(x)      for x in data[fin_futs_only_raw.lev_money_positions_long_all]                                           ]
        conv[fin_futs_only.leveraged_long_pct]      = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_lev_money_long_all]                                           ]
        conv[fin_futs_only.leveraged_short]         = [ int(x)      for x in data[fin_futs_only_raw.lev_money_positions_short_all]                                          ]
        conv[fin_futs_only.leveraged_short_pct]     = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_lev_money_short_all]                                          ]
        conv[fin_futs_only.leveraged_spead]         = [ int(x)      for x in data[fin_futs_only_raw.lev_money_positions_spread_all]                                         ]
        conv[fin_futs_only.leveraged_spread_pct]    = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_lev_money_spread_all]                                         ]
        conv[fin_futs_only.leveraged_net]           = [ conv[fin_futs_only.leveraged_long][i]       - conv[fin_futs_only.leveraged_short][i]        for i in range(n_recs)  ]
        conv[fin_futs_only.leveraged_net_pct]       = [ conv[fin_futs_only.leveraged_long_pct][i]   - conv[fin_futs_only.leveraged_short_pct][i]    for i in range(n_recs)  ]
        conv[fin_futs_only.other_long]              = [ int(x)      for x in data[fin_futs_only_raw.other_rept_positions_long_all]                                          ]
        conv[fin_futs_only.other_long_pct]          = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_other_rept_long_all]                                          ]
        conv[fin_futs_only.other_short]             = [ int(x)      for x in data[fin_futs_only_raw.other_rept_positions_short_all]                                         ]
        conv[fin_futs_only.other_short_pct]         = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_other_rept_short_all]                                         ]
        conv[fin_futs_only.other_spread]            = [ int(x)      for x in data[fin_futs_only_raw.other_rept_positions_spread_all]                                        ]
        conv[fin_futs_only.other_spread_pct]        = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_other_rept_spread_all]                                        ]
        conv[fin_futs_only.other_net]               = [ conv[fin_futs_only.other_long][i]       - conv[fin_futs_only.other_short][i]        for i in range(n_recs)          ]
        conv[fin_futs_only.other_net_pct]           = [ conv[fin_futs_only.other_long_pct][i]   - conv[fin_futs_only.other_short_pct][i]    for i in range(n_recs)          ]
        conv[fin_futs_only.nonrep_long]             = [ int(x)      for x in data[fin_futs_only_raw.nonrept_positions_long_all]                                             ]
        conv[fin_futs_only.nonrep_long_pct]         = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_nonrept_long_all]                                             ]
        conv[fin_futs_only.nonrep_short]            = [ int(x)      for x in data[fin_futs_only_raw.nonrept_positions_short_all]                                            ]
        conv[fin_futs_only.nonrep_short_pct]        = [ float(x)    for x in data[fin_futs_only_raw.pct_of_oi_nonrept_short_all]                                            ]
        conv[fin_futs_only.nonrep_net]              = [ conv[fin_futs_only.nonrep_long][i]      - conv[fin_futs_only.nonrep_short][i]       for i in range(n_recs)          ]
        conv[fin_futs_only.nonrep_net_pct]          = [ conv[fin_futs_only.nonrep_long_pct][i]  - conv[fin_futs_only.nonrep_short_pct][i]   for i in range(n_recs)          ]
        conv[fin_futs_only.oi]                      = [ int(x)      for x in data[fin_futs_only_raw.open_interest_all]                                                      ]


    elif report_type in [ report.futs_only, report.futs_and_opts ]:

        n_recs = len(data[futs_only_raw.as_of_date_in_form_yyyy_mm_dd])

        conv[futs_only.date]                = [ x           for x in data[futs_only_raw.as_of_date_in_form_yyyy_mm_dd]                              ]
        conv[futs_only.comm_long]           = [ int(x)      for x in data[futs_only_raw.commercial_positions_long_all]                              ]
        conv[futs_only.comm_long_pct]       = [ float(x)    for x in data[futs_only_raw.pct_of_oi_commercial_long_all]                              ]
        conv[futs_only.comm_short]          = [ int(x)      for x in data[futs_only_raw.commercial_positions_short_all]                             ]
        conv[futs_only.comm_short_pct]      = [ float(x)    for x in data[futs_only_raw.pct_of_oi_commercial_short_all]                             ]
        conv[futs_only.comm_net]            = [ conv[futs_only.comm_long][i]        - conv[futs_only.comm_short][i]     for i in range(n_recs)      ]
        conv[futs_only.comm_net_pct]        = [ conv[futs_only.comm_long_pct][i]    - conv[futs_only.comm_short_pct][i] for i in range(n_recs)      ]
        conv[futs_only.noncomm_long]        = [ int(x)      for x in data[futs_only_raw.noncommercial_positions_long_all]                           ]
        conv[futs_only.noncomm_long_pct]    = [ float(x)    for x in data[futs_only_raw.pct_of_oi_noncommercial_long_all]                           ]
        conv[futs_only.noncomm_short]       = [ int(x)      for x in data[futs_only_raw.noncommercial_positions_short_all]                          ]
        conv[futs_only.noncomm_short_pct]   = [ float(x)    for x in data[futs_only_raw.pct_of_oi_noncommercial_short_all]                          ]
        conv[futs_only.noncomm_spread]      = [ int(x)      for x in data[futs_only_raw.noncommercial_positions_spreading_all]                      ]
        conv[futs_only.noncomm_spread_pct]  = [ float(x)    for x in data[futs_only_raw.pct_of_oi_noncommercial_spreading_all]                      ]
        conv[futs_only.noncomm_net]         = [ conv[futs_only.noncomm_long][i]     - conv[futs_only.noncomm_short][i]      for i in range(n_recs)  ]
        conv[futs_only.noncomm_net_pct]     = [ conv[futs_only.noncomm_long_pct][i] - conv[futs_only.noncomm_short_pct][i]  for i in range(n_recs)  ]
        conv[futs_only.nonrep_long]         = [ int(x)      for x in data[futs_only_raw.nonreportable_positions_long_all]                           ]
        conv[futs_only.nonrep_long_pct]     = [ float(x)    for x in data[futs_only_raw.pct_of_oi_nonreportable_long_all]                           ]
        conv[futs_only.nonrep_short]        = [ int(x)      for x in data[futs_only_raw.nonreportable_positions_short_all]                          ]
        conv[futs_only.nonrep_short_pct]    = [ float(x)    for x in data[futs_only_raw.pct_of_oi_nonreportable_short_all]                          ]
        conv[futs_only.nonrep_net]          = [ conv[futs_only.nonrep_long][i]      - conv[futs_only.nonrep_short][i]       for i in range(n_recs)  ]
        conv[futs_only.nonrep_net_pct]      = [ conv[futs_only.nonrep_long_pct][i]  - conv[futs_only.nonrep_short_pct][i]   for i in range(n_recs)  ]
        conv[futs_only.oi]                  = [ int(x) for x in data[futs_only_raw.open_interest_all]                                               ]

    elif report_type == report.cit_supp:

        n_recs = len(data[futs_only_raw.as_of_date_in_form_yyyy_mm_dd])

        conv[cit_supp.date]                 = [ x           for x in data[cit_supp_raw.as_of_date_in_form_yyyy_mm_dd]                               ]
        conv[cit_supp.noncomm_long]         = [ int(x)      for x in data[cit_supp_raw.ncomm_positions_long_all_nocit]                              ]
        conv[cit_supp.noncomm_long_pct]     = [ float(x)    for x in data[cit_supp_raw.pct_oi_noncomm_long_all_nocit]                               ]
        conv[cit_supp.noncomm_short]        = [ int(x)      for x in data[cit_supp_raw.ncomm_positions_short_all_nocit]                             ]
        conv[cit_supp.noncomm_short_pct]    = [ float(x)    for x in data[cit_supp_raw.pct_oi_noncomm_short_all_nocit]                              ]
        conv[cit_supp.noncomm_spread]       = [ int(x)      for x in data[cit_supp_raw.ncomm_postions_spread_all_nocit]                             ]
        conv[cit_supp.noncomm_spread_pct]   = [ float(x)    for x in data[cit_supp_raw.pct_oi_noncomm_spread_all_nocit]                             ]
        conv[cit_supp.noncomm_net]          = [ conv[cit_supp.noncomm_long][i]      - conv[cit_supp.noncomm_short][i]       for i in range(n_recs)  ]
        conv[cit_supp.noncomm_net_pct]      = [ conv[cit_supp.noncomm_long_pct][i]  - conv[cit_supp.noncomm_short_pct][i]   for i in range(n_recs)  ]
        conv[cit_supp.comm_long]            = [ int(x)      for x in data[cit_supp_raw.comm_positions_long_all_nocit]                               ]
        conv[cit_supp.comm_long_pct]        = [ float(x)    for x in data[cit_supp_raw.pct_oi_comm_long_all_nocit]                                  ]
        conv[cit_supp.comm_short]           = [ int(x)      for x in data[cit_supp_raw.comm_positions_short_all_nocit]                              ]
        conv[cit_supp.comm_short_pct]       = [ float(x)    for x in data[cit_supp_raw.pct_oi_comm_short_all_nocit]                                 ]
        conv[cit_supp.comm_net]             = [ conv[cit_supp.comm_long][i]     - conv[cit_supp.comm_short][i]      for i in range(n_recs)          ]
        conv[cit_supp.comm_net_pct]         = [ conv[cit_supp.comm_long_pct][i] - conv[cit_supp.comm_short_pct][i]  for i in range(n_recs)          ]
        conv[cit_supp.nonrep_long]          = [ int(x)      for x in data[cit_supp_raw.nonrept_positions_long_all]                                  ]
        conv[cit_supp.nonrep_long_pct]      = [ float(x)    for x in data[cit_supp_raw.pct_oi_nonrept_long_all_nocit]                               ]
        conv[cit_supp.nonrep_short]         = [ int(x)      for x in data[cit_supp_raw.nonrept_positions_short_all]                                 ]
        conv[cit_supp.nonrep_short_pct]     = [ float(x)    for x in data[cit_supp_raw.pct_oi_nonrept_short_all_nocit]                              ]
        conv[cit_supp.nonrep_net]           = [ conv[cit_supp.nonrep_long][i]       - conv[cit_supp.nonrep_short][i]        for i in range(n_recs)  ]
        conv[cit_supp.nonrep_net]           = [ conv[cit_supp.nonrep_long_pct][i]   - conv[cit_supp.nonrep_short_pct][i]    for i in range(n_recs)  ]
        conv[cit_supp.cit_long]             = [ int(x)      for x in data[cit_supp_raw.cit_positions_long_all]                                      ]
        conv[cit_supp.cit_long_pct]         = [ float(x)    for x in data[cit_supp_raw.pct_oi_cit_long_all]                                         ]
        conv[cit_supp.cit_short]            = [ int(x)      for x in data[cit_supp_raw.cit_positions_short_all]                                     ]
        conv[cit_supp.cit_short_pct]        = [ float(x)    for x in data[cit_supp_raw.pct_oi_cit_short_all]                                        ]
        conv[cit_supp.cit_net]              = [ conv[cit_supp.cit_long][i]     - conv[cit_supp.cit_short][i]        for i in range(n_recs)          ]
        conv[cit_supp.cit_net_pct]          = [ conv[cit_supp.cit_long_pct][i] - conv[cit_supp.cit_short_pct][i]    for i in range(n_recs)          ]
        conv[cit_supp.oi]                   = [ int(x) for x in data[cit_supp_raw.open_interest_all]                                                ]

    return conv


def get_index(report_type: int):

    res = get(f"{API_ROOT}/{REPORT_STR[report_type]}/index")

    return res.json()


def get_contract(
    report_type:    int, 
    code_or_symbol: str, 
    fmt:            int,
    start_date:     str = None,
    end_date:       str = None
):

    code = code_or_symbol

    if code_or_symbol in COMMON_SYMBOLS:

        code = COMMON_SYMBOLS[code_or_symbol]

    res     = get(f"{API_ROOT}/{REPORT_STR[report_type]}/{code}")
    data    = res.json()
    headers = list(data.keys())
    cols    = list(data.values())
    i       = 0
    j       = len(cols[0]) # all cols should be the same length

    if start_date:

        # all reports have YYYY-MM-DD in 2nd col.
        # however, for some this is the date of the report report (friday); 
        # for others, it is the "as of" date (i.e. tuesday).

        i = bisect_left(data[headers[DATE_KEY]], start_date)

    if end_date:

        j = bisect_left(data[headers[DATE_KEY]], end_date)

    data = {
        header: col[i:j]
        for header, col in data.items()
    }

    if fmt != format.none:

        cols = list(data.values())
        data = {
            i : cols[i]
            for i in range(len(headers))
        }
    
        if fmt == format.convenience:

            data = convenience_recs(report_type, data)

    return data