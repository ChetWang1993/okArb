system("l qml.q");

// normalize: {[agg; names] ![agg; (); 0b; names!({(%; x; (dev; x))} each names)]};
replace0n: { (x where x = 0n): 0f; x };
noutlier: {((x = 0nf) + (x = 0wf) + (x = -0wf)) = 0};
capFloor: { max (x; min(y; z)) };
sq: { x xexp 2 };
autocorr: {[lags; s] {x[0] cor x[1] xprev x[0]} each (enlist s) ,/: lags };
fifo: { (+\)(((+\)y)?(+\)x) = (#)y };
/ skew: { avg 3 xexp (x - avg x) % dev x };
skew: { (sum 3 xexp x) % (1.5 xexp sum x * x) };
herfindahl: { (sum sq x) % sq sum x };
rosenbluth: { reciprocal 2 * (sum (1 + rank x) * (x % sum x)) - 1 };
gini: { (sum abs (x cross x)[; 1] - (x cross x)[; 0]) % 2 * avg x * sq count x };
robinhood: { (sum abs (x - med x)) % avg x };
qtln:{[x;y;z]cf:(0 1;1%2 2;0 0;1 1;1%3 3;3%8 8) z-4;n:count y:asc y;
    ?[hf<1;first y;last y]^y[hf-1]+(h-hf)*y[hf]-y -1+hf:floor h:cf[0]+x*n+1f-sum cf};
qtl: qtln[;;4];
normalize: {[x] {[a; d; x] (x - a) % d }[avg x; dev x] each x };
normalize_w: {[x; w] {[a; d; x]
    (x - a) % d }[w wavg x; sqrt (w wavg x * x) - (w wavg x) * (w wavg x)] each x };
normalize_agg: {[agg; names] ![agg; (); (enlist`date)!enlist`date; names!({(%; x; (dev; x))} each names)]};
replace0w: { (x where 0w = abs x ): 0n; x };
msharpe: { replace0w (sqrt 250) * mavg[x; y] % mdev[x; y] };
sharpe: {(sqrt 250) * avg[x] % dev[x] };
mret: { replace0w mavg[x; y] };
mskew: {[d; x] d mavg 3 xexp (x - mavg[d; x]) % mdev[d; x] };
sliding_ret: { replace0n msum[x; y] % msum[x; z] };
sw: { { 1_x, y } \ [x#0; y] };
corr_alpha: {[x; y] (cor/)(x; y)[; where (&/) 0 <> (x; y)] };
corr_matrix: {[t; ks] 0f^u corr_alpha/:\:u:(0!t) ks };
table_splitter: {[data] {?[x; cols[y] {(=; x; y)}' value y; 0b; ()]}[data] each distinct ?[data; (); 0b; {x!x} key data] };

reg_simple: {[t]
    system("l qml.q");
    tab2mat: { flip value flip x };
    y: tab2mat select y from t;
    cls: key flip delete y from t;
    x: tab2mat delete y from t;
    w: .qml.mlsq[x; y];
    y1: .qml.mm[x; w];
    t1: update err: y - est from update est: first each y1 from t;
    SSres: d * d: exec dev err from t1;
    SStot: d * d: exec dev y from t1;
    t2: update r2: 1 - SSres % SStot from flip cls!w };

reg: {[t]
    r: reg_simple t;
    names: 1_prev cols r;
    stdevs: value ?[t; (); (); names!{(dev; x)} each names];
    pref_names: { `$y ,/: string x }[names];
    betas_query: pref_names["beta_"]!names;
    stdevs_query: pref_names["stdev_"]!enlist each stdevs;
    biases_query: pref_names["bias_"]!({ (*; x; enlist y) } .) each names, 'stdevs;
    r2_query: (enlist `r2)!enlist `r2;
    query: betas_query, stdevs_query, biases_query, r2_query;
    ?[r; (); 0b; query] };
    
reg_intercept: {[t] reg update intercept: 1 from t };
reg_alpha: {[t; x; p] raze {[t; x; p] t: ![t; (); 0b; `alpha`perf!(x; p)];
    update alpha: x from reg select y: 1e4 * perf, alpha from t where not null perf, not null alpha }[t;;p] each x };
reg_axis: {[t; axis]
    axis: first keys t;
    aux: {
        r: reg_intercept ?[x; (); 0b; {x!x} cols[x] except keys x];
        q: first flip ?[x; (); (); keys[x]!keys x];
        ![r; (); 0b; q] };
    res: $[1 > count keys t; reg_intercept t; raze aux each table_splitter t];
    ?[res; (); 0b; (axis; `bias_alpha)!(axis; `bias_alpha)] };
mf_clause: {[xs; betas]
    k: first xs;
    if[1 = count xs; :(*; k; first[betas[`$"beta_", string k]])];
    (+; (*; k; first[betas[`$"beta_", string k]]); mf_clause[1_xs; betas]) };
bias_clause: {[xs]
    k: first xs;
    if[1 = count xs; :`$"bias_", string k];
    (+; `$"bias_", string k; bias_clause[1_xs]) };