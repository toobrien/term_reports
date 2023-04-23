from enum import IntEnum


class disagg_futs_only(IntEnum):

    date                = 0
    prod_merc_long      = 1
    prod_merc_long_pct  = 2
    prod_merc_short     = 3
    prod_merc_short_pct = 4
    prod_merc_net       = 5
    prod_merc_net_pct   = 6
    swap_long           = 7
    swap_long_pct       = 8
    swap_short          = 9
    swap_short_pct      = 10
    swap_spread         = 11
    swap_spread_pct     = 12
    swap_net            = 13
    swap_net_pct        = 14
    managed_long        = 15
    managed_long_pct    = 16
    managed_short       = 17
    managed_short_pct   = 18
    managed_spread      = 19
    managed_spread_pct  = 20
    managed_net         = 21
    managed_net_pct     = 22
    other_long          = 23
    other_long_pct      = 24
    other_short         = 25
    other_short_pct     = 26
    other_spread        = 27
    other_spread_pct    = 28
    other_net           = 29
    other_net_pct       = 30
    nonrep_long         = 31
    nonrep_long_pct     = 32
    nonrep_short        = 33
    nonrep_short_pct    = 34
    nonrep_net          = 35
    nonrep_net_pct      = 36
    oi                  = 37


class fin_futs_only(IntEnum):

    date                    = 0
    dealer_long             = 1
    dealer_long_pct         = 2
    dealer_short            = 3
    dealer_short_pct        = 4
    dealer_spread           = 5
    dealer_spread_pct       = 6
    dealer_net              = 7
    dealer_net_pct          = 8
    asset_mgr_long          = 9
    asset_mgr_long_pct      = 10
    asset_mgr_short         = 11
    asset_mgr_short_pct     = 12
    asset_mgr_spread        = 13
    asset_mgr_spread_pct    = 14
    asset_mgr_net           = 15
    asset_mgr_net_pct       = 16
    leveraged_long          = 17
    leveraged_long_pct      = 18
    leveraged_short         = 19
    leveraged_short_pct     = 20
    leveraged_spead         = 21
    leveraged_spread_pct    = 22
    leveraged_net           = 23
    leveraged_net_pct       = 24
    other_long              = 25
    other_long_pct          = 26
    other_short             = 27
    other_short_pct         = 28
    other_spread            = 29
    other_spread_pct        = 30
    other_net               = 31
    other_net_pct           = 32
    nonrep_long             = 33
    nonrep_long_pct         = 34
    nonrep_short            = 35
    nonrep_short_pct        = 36
    nonrep_net              = 37
    nonrep_net_pct          = 38
    oi                      = 39


class futs_only(IntEnum):

    date                = 0
    comm_long           = 1
    comm_long_pct       = 2
    comm_short          = 3
    comm_short_pct      = 4
    comm_net            = 5
    comm_net_pct        = 6
    noncomm_long        = 7
    noncomm_long_pct    = 8
    noncomm_short       = 9
    noncomm_short_pct   = 10
    noncomm_spread      = 11
    noncomm_spread_pct  = 12
    noncomm_net         = 13
    noncomm_net_pct     = 14
    nonrep_long         = 15
    nonrep_long_pct     = 16
    nonrep_short        = 17
    nonrep_short_pct    = 18
    nonrep_net          = 19
    nonrep_net_pct      = 20
    oi                  = 21


class cit_supp(IntEnum):

    date                = 0
    noncomm_long        = 1
    noncomm_long_pct    = 2
    noncomm_short       = 3
    noncomm_short_pct   = 4
    noncomm_spread      = 5
    noncomm_spread_pct  = 6
    noncomm_net         = 7
    noncomm_net_pct     = 8
    comm_long           = 9
    comm_long_pct       = 10
    comm_short          = 11
    comm_short_pct      = 12
    comm_net            = 13
    comm_net_pct        = 14
    nonrep_long         = 15
    nonrep_long_pct     = 16
    nonrep_short        = 17
    nonrep_short_pct    = 18
    nonrep_net          = 19
    nonrep_net_pct      = 20
    cit_long            = 21
    cit_long_pct        = 22
    cit_short           = 23
    cit_short_pct       = 24
    cit_net             = 25
    cit_net_pct         = 26
    oi                  = 27


# these record types are the same

disagg_futs_and_opts    = disagg_futs_only
fin_futs_and_opts       = fin_futs_only
futs_and_opts           = futs_only