#!/root/q/l64/q
/#!/Users/apple/q/m64/q
pwds: "/" vs {value[.z.s]}[][6];
script_path: "/" sv _[pwds; count[pwds] - 1];
system("l ", script_path, "/utils.q");
system("l ", script_path, "/alpha_stats.q");
args: .Q.def[(1#`dt)!1#.z.d].Q.opt .z.x;
d: args`dt;

if[not is_bday d; exit 0];
if[not file_exists script_path, "/../data/compo/", date_to_str[d], ".txt"; exit 0];
read_if_exists: {[p; f; names]
    if[not file_exists p; t: ("SF"; enlist "\t") 0: hsym `$script_path, "/../data/compo/", date_to_str[d], ".txt"; :![t; (); 0b; names!{ ( 0f ) } each names]];
    (f; enlist "\t") 0:hsym `$p };
alpha_lj: {[t1; t2] $[() ~ t1; t2; not () ~ t2; t1 lj `ric xkey t2; t1] };
alphas: alpha_lj[(); read_if_exists[script_path, "/../data/alpha/pv/", date_to_str[d], ".txt"; "SF"; 1#`pv_neg]];
alphas: alpha_lj[alphas; read_if_exists[script_path, "/../data/alpha/ccass/alpha/", date_to_str[d], ".txt"; "SFFFFF"; `doubleWeightedFlow`ccn_var]];
alphas: alpha_lj[alphas; read_if_exists[script_path, "/../data/alpha/fund/", date_to_str[d], ".txt"; "SFFFFFF"; 1#`fund1]];
alphas: alpha_lj[alphas; read_if_exists[script_path, "/../data/alpha/hf/", date_to_str[d], ".txt"; "SFFF"; `down_vol`open_volume]];
if[0 = count alphas; show "no mf alpha on ", date_to_str d; exit 0];
erd: raze get_erd each get_bday_range[d - 50; d - 1];
if[0 = count erd; exit 0];
erd: update_erd erd;
erd: select from erd where date = max date, not null adv;
alphas: alphas lj `ric xkey erd;
betas: ();
betas.pv_neg: 50;
betas.fund1: 30;
betas.down_vol: 20;
betas.open_volume: 35;
betas.doubleWeightedFlow: 35;
betas.ccn_var: 30;
ks: raze `pv_neg`fund1`down_vol`open_volume`doubleWeightedFlow`ccn_var;
alphas: ![alphas; (); 0b; ks!{ (replace0n; x) } each ks];
alphas: ![alphas; (); 0b; enlist[`mf]!enlist mf_clause[ks; betas]];
output_path: script_path, "/../data/alpha/mf/", date_to_str[d], ".txt";
show output_path;
(hsym `$output_path) 0: "\t" 0: select ric, mf, replace0n adv from alphas;
exit 0;

