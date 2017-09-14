#Fucntions for Creating Social Media Dashboarh
import nltk
import pandas as pd
import sys
from bokeh.plotting import figure
from bokeh.charts import Bar, Scatter, output_file, show, ColumnDataSource
from bokeh.layouts import row, column
from bokeh.models import HoverTool
from matplotlib import colors
from collections import Counter

def nuvi(data):
	"""Break nuvi data into smaller component pieces, english, and twitter only data"""

	dat_small = data[["Author", "Text", "Lang", "IsReshare", "Reach", "Influence", "Network", "Sentiment"]]
	dat_eng = dat_small[dat_small["Lang"] == 'en']
	no_rss = dat_eng[dat_eng["Network"] != "RSS"]
	nuvi_dat = True

	return dat_small, dat_eng, no_rss, nuvi_dat

def plot_nets(data):
	"""Create a barchart for the frequency of posts on social media outlets via Nuvi data"""
	net_counts = pd.DataFrame(data["Network"].value_counts())
	net_counts["Net"] = net_counts.index
	netfig = figure()
	nets = Bar(net_counts, "Net", values = 'Network', title = 'Social Network Activity', color = 'Net')

	nets.xaxis.axis_label = "Network"

#	output_file('barchart.html')
#	show(nets)
	return nets


def max_nuvi_stats(data, n=20):
	"""This function pulls out the users with the top reach and influence,
	combines the two sets, and removes duplicates. The combined data frame is returned
	with an annotation for the set that it comes from to then be graphed and added
	to a dashboard."""
	gb_auth = pd.groupby(data, "Author").sum()
	max_reach = gb_auth["Reach"].sort_values(ascending = False)
	max_inf = gb_auth["Influence"].sort_values(ascending=False)
	top_reach_index = max_reach[0:(n-1)].index
	top_inf_index = max_inf[0:(n-1)].index
	top_reach = gb_auth.ix[top_reach_index]
	top_inf = gb_auth.ix[top_inf_index]
	in_both = set(top_reach_index).intersection(top_inf_index)
	in_one = set(top_reach_index).union(top_inf_index)
	top_reach["set"] = "Reach"
	top_inf["set"] = "Influence"
	top_social = top_reach.append(top_inf)
	top_social = top_social[~top_social.index.duplicated(keep='first')]
	top_social.loc[in_both,'set'] = "Both"
	return top_social


###This color mapper didn't pan out but I feel like it could be useful at some point

def color_mapping(data = top_social, col_to_map = 'set'):
	"""Automatically create a color map for plotting based on an unknown number
	of groups"""
	cols = list(colors.cnames.items())
	cname, hexa = zip(*cols)
	uni = data[col_to_map].unique()
	uni_len = len(uni)
	col = cname[0:uni_len]
	mapper = dict(zip(uni, col))
	return mapper

#col_map = color_mapping()

def plot_nuvi_stats(data, x = 'Reach', y = 'Influence', 
	title = 'Users with Top Social Reach and Influence', 
	xlabel = 'Reach', ylabel = 'Influence', color = ['green', 'blue', 'red']):
	"""Create a scatter plot with hover tools for the top influencers and 
	users with the greatest reach. Hovering over each point will provide 
	The reach, influence (both plotted), which set they belong to, and the 
	number of reshares the had"""
	
	cds1 = ColumnDataSource(data[data["set"]=='Both'])
	cds2 = ColumnDataSource(data[data["set"]=='Reach'])
	cds3 = ColumnDataSource(data[data["set"]=='Influence'])
	tt = HoverTool(tooltips=[
	('User', '@Author'),
	('Reshares', '@IsReshare'),
	('Reach', '@Reach'),
	('Influence', '@Influence'),
	('Group', '@set')])
	top = figure(x_axis_label = x, y_axis_label = y, x_axis_type = 'log', x_range = (0,max(data[x]*10)),
		title = title, tools = ['pan', 'save','wheel_zoom',tt,'box_select', 'lasso_select', 'reset'])
	top.circle(x = x, y = y, size = 10, source = cds1, color = color[0], legend = "Both")
	top.square(x = x, y = y, size = 10, source = cds2, color = color[1], legend = "Reach")
	top.triangle(x = x, y = y, size = 10, source = cds3, color = color[2], legend = "Influence")
	top.legend.location='top_left'
	
#	show(top)
#	output_file("tops.html")
	return top

def count_posts(data, n=30):
	"""Returns n users with the most posts"""
	post_counts = pd.DataFrame(data["Author"].value_counts())[0:n]
	return post_counts


def plot_count_posts(data, x_label = "Number of Tweets", title = "Highest Tweeting Users"):
	"""Make a horizontal bar chart of the users who post the most social media"""
	auth_fig = figure(x_axis_label = "Number of Tweets", y_axis_label = "User",
		y_range = count_posts(data).index.tolist(), title = title)
	auth_fig.hbar(y = count_posts(data).index, height = .5, left = 0, right = count_posts(data)["Author"])
#	show(auth_fig)
	print(count_posts(data))
	return auth_fig



if __name__ == "__main__":
	f = sys.argv[1]
	n = int(sys.argv[2])
	output = sys.argv[3]
	nuvi_dat = False

	dat = pd.read_csv(f)
	dat_small, dat_eng, twit, nuvi_dat = nuvi(data = dat)
	top_social = max_nuvi_stats(data = dat_small, n=n)
	top_social["Author"] = top_social.index

	p1 = plot_nets(data = dat_small)
	p2 = plot_nuvi_stats(data = top_social)
	p3 = plot_count_posts(data = twit)

	p = row(column(p1, p3), p2)
	output_file(output)
	show(p)

