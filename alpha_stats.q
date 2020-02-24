pwds: "/" vs {value[.z.s]}[][6];
system("cd /Users/apple/Documents/trading/scripts/");
system("l qrtools.q");
system("l utils.q");
dailypnl: {[agg; names; perf]
    t: ?[normalize_agg[agg; names]; (); (enlist`date)!enlist`date; (names)!({[p; x] (sum; (*; p; (*; `clip; x)))}[perf;] each names)];
    `date xcols ?[t; (); 0b; (names, `date)!raze ({ (sums; x) } each names; `date)] };
get_extraday_perf_ex: {[t; c]
    perfs: `p1d`p2d`p3d`p4d`p10d`p19d;
    perf_horizons: (1; 2; 3; 4; 10; 19);
    t: ![t; (); 0b; (1#`alpha)!1#c];
    `horizon xcols update {"F"$.Q.f[3; x]} each perf, {"F"$.Q.f[3; x]} each sharpe from update perf: 1e4 * perf, horizon: perfs from {[t; perf_t]
        perf_columns: perf_t[0]; perf_h: perf_t[1];
        a: ![t; (); 0b; (enlist`perf)!enlist perf_columns];
        perf: exec sum clip * perf * alpha % sum abs clip * alpha from a;
        a:select sum_pnl: sum clip * perf * alpha by date from a;
        sharpe: exec (sqrt 252 % perf_h) * avg sum_pnl % dev sum_pnl from a;
        `perf`sharpe!(perf; sharpe) }[select from t where clip > 0;] each perfs, 'perf_horizons };
linearity: {[t; c; p]
    t: ![t; (); 0b; `alpha`perf!(c; p)];
    t: select from t where alpha <> 0, noutlier alpha;
    t: update perf: perf - avg perf from t;
    (`alpha; `$"barra perf vs alpha values") xcol delete r from select avg alpha, 1e4 * avg perf by r: 10 xrank alpha from t };
perf_bucket: {[t; c; b; p]
    t: ![t; (); 0b; `alpha`bucket`perf!(c; b; p)];
    select r from select avg bucket, perf: 1e4 * sum clip * perf * alpha % sum abs clip * alpha by r: 10 xrank bucket from t };
perf_bucket_acc: {[t; c; b; p]
    t: ![normalize_agg[t; raze c]; (); 0b; `alpha`bucket`perf!(c; b; p)];
    t: update perf - avg perf by date from t;
    t: update r: {`$"bucket_", string x} each r from
        select return: sum clip * perf * alpha % sum abs clip * alpha
        by date, r: 5 xrank bucket from t;
    ks: exec distinct r from t;
    exec ks#(r!return) by date: date from () xkey update sums return by r from t };
read_alpha: {[p; f; s]
    raze {[x; p; f; s]
        d: "D"$8#-4_x;
        file: p, date_to_str[d], ".txt";
        if[not file_exists[file]; :()];
        update date: d from (f; enlist s) 0: hsym `$file }[; p; f; s] each system("ls ", p) };
dump_alpha: {[t; p; s]
    dates: exec distinct date from t;
    {[t; p; s; d]
        t: select from t where date = d;
        dp: p, date_to_str[d], ".txt";
        .qtutil.dump_table_txt[delete date from t; dp; s] }[t; p; s] each dates };
dist: {[t; c; d]
    t: ?[t; (); 0b; enlist[`x]!1#c];
    total_n: count t;
    0!select count[i] % total_n by r: {[d; x] "F"$.Q.f[d; x] }[d] each x from t };
// get_profile: {[alphas; xs] {[alphas; x]
//     t: get_extraday_perf[alphas; x];
//     alphas: ?[alphas; (); 0b; enlist[`alpha]!1#x];
//     `alpha_name`avg`dev`perf_mc`perf_1d`perf_2d`perf_3d`sharpe_mc`sharpe_1d`sharpe_2d`sharpe_3d!raze (x; exec avg alpha from alphas;
//         exec dev alpha from alphas; exec perf from 4#t; exec sharpe from 4#t)) }[alphas] each xs };
get_profile_h_ex: {[t; xs] (uj/){[t; x]
    t: get_extraday_perf_ex[t; x];
    `horizon xkey x xcol select perf, horizon from t}[t] each xs };
update_erd: {[t]
    t: update prev_volume: prev volume,
        prev_close: prev close,
        adv: mavg[30; money],
        perf_intraday: (close - open) % open,
        perf_overnight: (xprev[-1; open] - close) % close,
        future_perf_1d: (xprev[-1; close] - close) % close,
        future_perf_2d: (xprev[-2; close] - close) % close,
        future_perf_3d: (xprev[-3; close] - close) % close,
        future_perf_4d: (xprev[-4; close] - close) % close,
        future_perf_10d: (xprev[-10; close] - close) % close,
        future_perf_19d: (xprev[-19; close] - close) % close by ric from t;
    t: update clip: { min (0.02 * x; 1e7) } each money from t;
    t: update intra: perf_intraday, p1d: future_perf_1d, p2d: future_perf_2d, p3d: future_perf_3d, p4d: future_perf_4d, p10d: future_perf_10d, p19d: future_perf_19d from t;
    t: update p1d: p1d + intra, p2d: p2d + intra, p3d: p3d + intra, p4d: p4d + intra, p10d: p10d + intra, p19d: p19d + intra from t;
    delete perf_intraday, future_perf_1d, future_perf_2d, future_perf_3d, future_perf_4d, future_perf_10d, future_perf_19d from t
    };