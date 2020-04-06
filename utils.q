// data_path: "/Users/apple/Documents/trading/data/";
data_path: "/root/data/";
trading_days_path: data_path, "/trading_days.txt";
compo_path: data_path, "/compo/";
erd_path: data_path, "/erd/";
ten_path: data_path, "/ten/";
date_to_str: {[d] ssr[string d; "."; ""] };
file_exists: { not () ~ key hsym `$x };
get_bday_range: {[sd; ed] days: (enlist "D"; enlist "\t") 0: hsym `$trading_days_path; (select from days where date >= sd, date <= ed)`date };
is_bday: { (0 <> first get_bday_range[x; x]) and (0 <> count get_bday_range[x; x]) };
bday_offset: {[d; offset]
    days: (enlist "D"; enlist "\t") 0: hsym `$trading_days_path;
    idx: offset + first exec i from days where date = d;
    (days`date)[idx]
    };
get_compo: { update date: x from ("SF"; enlist "\t") 0: `$compo_path, date_to_str[x], ".txt" };
get_erd: {
    data_path: erd_path, date_to_str[x], ".txt";
    if[not file_exists data_path; :()];
    lines: {"\t" vs x } each read0 hsym `$data_path;
    t: flip (`$lines[0])!flip { raze (`$x[0]; "D"$x[1]; "F"$2_x) } each 1_lines;
    select from t where date = x };
//    update date: x from flip (`$lines[0])!flip { raze (`$x[0]; "F"$1_x) } each 1_lines };
get_ten: {
    data_path: ten_path, date_to_str[x], ".txt";
    if[not file_exists data_path; :()];
    lines: {"\t" vs x } each read0 hsym `$data_path;
    t: flip (`$lines[0])!flip { raze (`$x[0]; "D"$x[1]; "F"$2_x) } each 1_lines;
    select from t where date = x };
piv:{[t;k;p;v]
    / controls new columns names
    f:{[v;P]`${raze " " sv x} each string raze P[;0],'/:v,/:\:P[;1]};
     v:(),v; k:(),k; p:(),p; / make sure args are lists
     G:group flip k!(t:.Q.v t)k;
     F:group flip p!t p;
     key[G]!flip(C:f[v]P:flip value flip key F)!raze
      {[i;j;k;x;y]
       a:count[x]#x 0N;
       a[y]:x y;
       b:count[x]#0b;
       b[y]:1b;
       c:a i;
       c[k]:first'[a[j]@'where'[b j]];
       c}[I[;0];I J;J:where 1<>count'[I:value G]]/:\:[t v;value F]};
update_erd: {[t]
    t: update prev_volume: prev volume,
        prev_close: prev close,
        adv: mavg[30; money],
        vol: mdev[30; close],
        perf_intraday: (close - open) % open,
        perf_overnight: (xprev[-1; open] - close) % close,
        future_perf_1d: (xprev[-1; close] - close) % close,
        future_perf_2d: (xprev[-2; close] - close) % close,
        future_perf_3d: (xprev[-3; close] - close) % close,
        future_perf_4d: (xprev[-4; close] - close) % close,
        future_perf_10d: (xprev[-10; close] - close) % close,
        future_perf_19d: (xprev[-19; close] - close) % close by ric from t;
    t: update clip: { min (0.02 * x; 1e7) } each adv from t;
    t: update intra: perf_intraday, p1d: future_perf_1d, p2d: future_perf_2d, p3d: future_perf_3d, p4d: future_perf_4d, p10d: future_perf_10d, p19d: future_perf_19d from t;
    t: update p1d: p1d + intra, p2d: p2d + intra, p3d: p3d + intra, p4d: p4d + intra, p10d: p10d + intra, p19d: p19d + intra from t;
    delete future_perf_1d, future_perf_2d, future_perf_3d, future_perf_4d, future_perf_10d, future_perf_19d from t
    };
calculate_beta: {[t]
    t[`perf]: t[`p19d];
    t: update mkt_perf: sum weight * perf by date from t;
    t: update tmp_cov: perf * mkt_perf, tmp_var: mkt_perf * mkt_perf from t where not null perf, not null mkt_perf;
    t: update tmp_prev_cov: prev tmp_cov, tmp_prev_var: prev tmp_var by ric from t;
    t: update tmp_count: 1i from t where not null tmp_prev_cov, not null tmp_prev_var;
    t: update sumcov: 252 msum tmp_prev_cov, sumvar: 252 msum tmp_prev_var, beta_count: 252 msum tmp_count from t;
    t: update beta: sumcov % sumvar from t where sumvar > 0f, beta_count > 125;
    delete tmp_cov, tmp_var, tmp_prev_cov, tmp_prev_var, tmp_count, sumcov, sumvar from t
    };
replace0n: { (x where x = 0n): 0f; x };
noutlier: {((x = 0nf) + (x = 0wf) + (x = -0wf) + (x = 0f)) = 0};
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
replace0w: { (x where 0w = abs x ): 0n; x };
msharpe: { replace0w (sqrt 250) * mavg[x; y] % mdev[x; y] };
sharpe: {(sqrt 250) * avg[x] % dev[x] };
mret: { replace0w mavg[x; y] };
mskew: {[d; x] d mavg 3 xexp (x - mavg[d; x]) % mdev[d; x] };
sliding_ret: { replace0n msum[x; y] % msum[x; z] };
sw: { { 1_x, y } \ [x#0; y] };
min_abs: {[x; y]
    if[(x >= 0) and y >= 0; :min(x; y)];
    if[(x >= 0) and y < 0; :0];
    if[(x < 0) and y >= 0; :0];
    if[(x < 0) and y < 0; :max(x; y)] };
rank_unique: .Q.fu[rank];
rank_gta: { m: rank_unique x; -1 + 2 * m % -1 + count m };
rank_alpha: {[alphas; x] ![alphas; enlist (noutlier; x); enlist[`date]!1#`date; enlist[x]!enlist (rank_gta; x)] };
corr_alpha: {[x; y] (cor/)(x; y)[; where (&/) 0 <> (x; y)] };
corr_matrix: {[t; ks] 0f^u corr_alpha/:\:u:(0!t) ks };
table_splitter: {[data] {?[x; cols[y] {(=; x; y)}' value y; 0b; ()]}[data] each distinct ?[data; (); 0b; {x!x} key data] };
