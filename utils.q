/ data_path: "/Users/apple/Documents/trading/stock/data/";
data_path: "/root/data/";
trading_days_path: data_path, "/trading_days.txt";
compo_path: data_path, "/compo/";
erd_path: data_path, "/erd/";
date_to_str: {[d] ssr[string d; "."; ""] };
file_exists: { not () ~ key hsym `$x };
get_bday_range: {[sd; ed] days: (enlist "D"; enlist "\t") 0: hsym `$trading_days_path; (select from days where date >= sd, date <= ed)`date };
is_bday: { 0 <> first get_bday_range[x; x] };
bday_offset: {[d; offset]
    days: (enlist "D"; enlist "\t") 0: hsym `$trading_days_path;
    idx: offset + first exec i from days where date = d;
    (days`date)[idx]
    };
get_compo: { ("SF"; enlist "\t") 0: `$compo_path, date_to_str[x], ".txt" };
get_erd: {
    data_path: erd_path, date_to_str[x], ".txt";
    if[not file_exists data_path; :()];
    lines: {"\t" vs x } each read0 hsym `$data_path;
    update date: x from flip (`$lines[0])!flip { raze (`$x[0]; "F"$1_x) } each 1_lines };
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
