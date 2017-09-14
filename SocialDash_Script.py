import SocialDash as soda
import pandas as pd
from bokeh.charts import output_file, show
from bokeh.layouts import row, column

f = 'C:\\Users\\Andrew\\Dropbox\\NVE\\Amazon\\NYCC 16\\Data\\NYCCNuviexp_MITHC_1001_1021.csv'
n = 30
nuvi_dat = False
output = "SoDash.html"

dat = pd.read_csv(f)
dat_small, dat_eng, twit, nuvi_dat = soda.nuvi(data = dat)
top_social = soda.max_nuvi_stats(data = dat_small, n=n)
top_social["Author"] = top_social.index

p1 = soda.plot_nets(data = dat_small)
p2 = soda.plot_nuvi_stats(data = top_social)
p3 = soda.plot_count_posts(data = twit)

p = row(column(p1, p3), p2)
output_file(output)
show(p)
