// data_path: "/Users/apple/Documents/trading/data/";
data_path: "/root/data/";
trading_days_path: data_path, "/trading_days.txt";
compo_path: data_path, "/compo/";
erd_path: data_path, "/erd/";
ten_path: data_path, "/ten/";
fund_path: data_path, "/fund/";
date_to_str: {[d] ssr[string d; "."; ""] };
file_exists: { not () ~ key hsym `$x };
get_bday_range: {[sd; ed] days: (enlist "D"; enlist "\t") 0: hsym `$trading_days_path; (select from days where date >= sd, date <= ed)`date };
is_bday: { (0 <> first get_bday_range[x; x]) and (0 <> count get_bday_range[x; x]) };
get_bday_offset: {[d; offset]
    days: (enlist "D"; enlist "\t") 0: hsym `$trading_days_path;
    first exec offset_date from (select date, offset_date: xprev[-1 * offset; date] from days) where date = d  };
bday_offset: {[d; offset]
    days: (enlist "D"; enlist "\t") 0: hsym `$trading_days_path;
    idx: offset + first exec i from days where date = d;
    (days`date)[idx]
    };
get_compo: {[cs; x] raze {[c; x] update date: x, compo: c from ("SF"; enlist "\t") 0: `$compo_path, string[c], "/", date_to_str[x], ".txt"}[; x] each cs };
get_erd: {[x; idx]
    data_path: erd_path, "/", idx, "/", date_to_str[x], ".txt";
    if[not file_exists data_path; :()];
    lines: {"\t" vs x } each read0 hsym `$data_path;
    t: flip (`$lines[0])!flip { raze (`$x[0]; "D"$x[1]; "F"$2_x) } each 1_lines;
    t: select from t where not null close;
    select from t where date = x };
get_fund: {
    data_path: fund_path, date_to_str[x], ".txt";
    if[not file_exists data_path; :()];
    lines: {"\t" vs x } each read0 hsym `$data_path;
    t: flip (`$lines[0])!flip { raze ("D"$x[0]; `$x[1]; "F"$2_x) } each 1_lines;
    select from t where date = x };
adj: {[t]
    fund: select date, ric, capi: capitalization from raze get_fund each distinct t`date;
    fund: update adj_factor: 1^next[capi] % capi by ric from fund;
    select from fund where adj_factor <> 1
    fund: `date xasc update adj_factor: (*\) adj_factor by ric from `date xdesc fund;
    update open: open % adj_factor, close: close % adj_factor, high: high % adj_factor, low: low % adj_factor from t lj `ric`date xkey fund
    };
filter_compo: {[t; cs]
    compo: raze get_compo[cs] each distinct t`date;
    select from (t lj `ric`date xkey compo) where not null weight
    };
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
    t: select from t where not null close;
    t: update prev_volume: prev volume,
        prev_close: prev close,
        adv: mavg[30; money],
        past_perf_overnight: (open - prev[close]) % prev[close],
        past_perf_1d: (close - xprev[1; close]) % xprev[1; close],
        past_perf_2d: (close - xprev[2; close]) % xprev[2; close],
        past_perf_3d: (close - xprev[3; close]) % xprev[3; close],
        past_perf_5d: (close - xprev[5; close]) % xprev[5; close],
        past_perf_10d: (close - xprev[10; close]) % xprev[10; close],
        past_perf_19d: (close - xprev[19; close]) % xprev[19; close],
        perf_intraday: (close - open) % open,
        perf_overnight: (xprev[-1; open] - close) % close,
        future_perf_1d: (xprev[-1; close] - close) % close,
        future_perf_2d: (xprev[-2; close] - close) % close,
        future_perf_3d: (xprev[-3; close] - close) % close,
        future_perf_5d: (xprev[-5; close] - close) % close,
        future_perf_10d: (xprev[-10; close] - close) % close,
        future_perf_19d: (xprev[-19; close] - close) % close by ric from t;
    t: update vol: mdev[30; past_perf_1d] by ric from t;
    t: update clip: "f"${ min ("i"$0.02 * x; 1e7) } each adv from t;
    t: update povernight: past_perf_overnight, pp1d: past_perf_1d, pp2d: past_perf_2d, pp3d: past_perf_3d, pp5d: past_perf_5d, pp10d: past_perf_10d, pp19d: past_perf_19d,
        intra: perf_intraday, overnight: perf_overnight, p1d: future_perf_1d, p2d: future_perf_2d, p3d: future_perf_3d, p5d: future_perf_5d, p10d: future_perf_10d, p19d: future_perf_19d from t;
    t: update p1d: p1d + intra, p2d: p2d + intra, p3d: p3d + intra, p5d: p5d + intra, p10d: p10d + intra, p19d: p19d + intra from t;
    delete past_perf_overnight, past_perf_1d, past_perf_2d, past_perf_3d, past_perf_5d, past_perf_10d, past_perf_19d,
        perf_intraday, perf_overnight, future_perf_1d, future_perf_2d, future_perf_3d, future_perf_5d, future_perf_10d, future_perf_19d from t
    };
replace0n: { (x where x = 0n): 0f; x };
/ noutlier: {((x = 0nf) + (x = 0wf) + (x = -0wf) + (x = 0f)) = 0};
noutlier: { x: "f"$x; ((x = 0nf) + (x = 0wf) + (x = -0wf) + (x = 0f)) = 0 };
capFloor: { max (x; min(y; z)) };
sq: { x xexp 2 };
autocorr: {[lags; s] {x[0] cor x[1] xprev x[0]} each (enlist s) ,/: lags };
fifo: { (+\)(((+\)y)?(+\)x) = (#)y };
skew: { avg 3 xexp (x - avg x) % dev x };
herfindahl: { (sum sq x) % sq sum x };
rosenbluth: { reciprocal 2 * (sum (1 + rank x) * (x % sum x)) - 1 };
gini: { (sum abs (x cross x)[; 1] - (x cross x)[; 0]) % 2 * avg x * sq count x };
robinhood: { (sum abs (x - med x)) % avg x };
qtln:{[x;y;z]cf:(0 1;1%2 2;0 0;1 1;1%3 3;3%8 8) z-4;n:count y:asc y;
    ?[hf<1;first y;last y]^y[hf-1]+(h-hf)*y[hf]-y -1+hf:floor h:cf[0]+x*n+1f-sum cf};
qtl: qtln[;;5];
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
rank_gta: {[start; multi; x] m: rank_unique x; start + multi * m % -1 + count m };
rank_alpha: {[alphas; x]
    alphas: ![alphas; enlist (noutlier; x); enlist[`date]!1#`date; enlist[x]!enlist (rank_gta[-1; 2]; x)];
    ![alphas; (); 0b; enlist[x]!enlist (^; 0; x)] };
corr_alpha: {[x; y] (cor/)(x; y)[; where (&/) 0 <> (x; y)] };
corr_matrix: {[t; ks] 0f^u corr_alpha/:\:u:(0!t) ks };
table_splitter: {[data] {?[x; cols[y] {(=; x; y)}' value y; 0b; ()]}[data] each distinct ?[data; (); 0b; {x!x} key data] };
calculate_beta: {[t; lookback; perf; c]
    min_days: "i"$lookback % 2;
    t[`perf]: t[perf];
    t: update mkt_perf: sum weight * perf by date from t;
    t: update tmp_cov: perf * mkt_perf, tmp_var: mkt_perf * mkt_perf from t where not null perf, not null mkt_perf;
    t: update tmp_prev_cov: prev tmp_cov, tmp_prev_var: prev tmp_var by ric from t;
    t: update tmp_count: 1i from t where not null tmp_prev_cov, not null tmp_prev_var;
    t: update sumcov: lookback msum tmp_prev_cov, sumvar: lookback msum tmp_prev_var, beta_count: lookback msum tmp_count from t;
    t: update beta_name: sumcov % sumvar from t where sumvar > 0f, beta_count > min_days;
    t[c]: t[`beta_name];
    delete tmp_cov, tmp_var, tmp_prev_cov, tmp_prev_var, tmp_count, sumcov, sumvar, beta_name from t };
filter_dict: {[dict; ks; filter; cap]
    raze {[dict; x; filter; cap] v: dict[x]; $[v < filter; ()!(); enlist[x]!1#cap&dict[x]] }[dict;; filter; cap] each ks };
top_elements: {[n; l] l: l[til n]; l where not null l };
apply_mavg: {[t; ks; duration] if[0 = count ks; :t]; ![t; (); enlist[`ric]!1#`ric; ks!{[duration; x] x; (mavg; duration; x) }[duration] each ks] };
apply_diff: {[t; ks; duration] if[0 = count ks; :t]; ![t; (); enlist[`ric]!1#`ric; ks!{[duration; x] (-; x; (mavg; duration; x)) }[duration] each ks] };
neutral_by: {[t; c; ks]
    cs: distinct ?[t; (); (); c];
    f: $[11 = type cs; like; =];
    if[11 = type cs; cs: string cs];
    raze {[t; c; ks; f; x] ?[t; enlist (f; c; x); 0b; ()] rank_alpha[;]/ ks }[t; c; ks; f] each cs };
sb_factor: {[alphas; x]
    alphas: ![alphas; enlist (noutlier; x); enlist[`date]!1#`date; enlist[`$string[x], "_sb"]!enlist (rank_gta[1 % 3; 2 % 3]; x)];
    ![alphas; (); 0b; enlist[x]!enlist (^; 0; x)] };
