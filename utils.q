/data_path: "/Users/apple/Documents/trading/alpha/data/";
data_path: "/root/data/prod/";
trading_days_path: data_path, "/trading_days.txt";
compo_path: data_path, "/compo/";
erd_path: data_path, "/erd/";
date_to_str: {[d] ssr[string d; "."; ""] };
file_exists: { not () ~ key hsym `$x };
get_bday_range: {[sd; ed] days: (enlist "D"; enlist "\t") 0: hsym `$trading_days_path; (select from days where date >= sd, date <= ed)`date };
is_bday: { 0 <> first get_bday_range[x; x] };
get_compo: { ("SF"; enlist "\t") 0: `$compo_path, date_to_str[x], ".txt" };
get_erd: {
    lines: {"\t" vs x } each read0 hsym `$erd_path, date_to_str[x], ".txt";
    flip (`$lines[0])!flip { raze (`$x[0]; "F"$1_x) } each 1_lines };
