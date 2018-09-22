import matplotlib
matplotlib.use('Agg')  # run matplotlib headless (for virtualenv)
import matplotlib.pyplot as plt # now we can import pyplot also headless
import numpy as np
import time


TMP_FILENAME = 'homesens/static/images/tmp_plot_collection.png'

def select_data_span(data, span):
	
	spans = np.array([24, 24*7, 24*7*30]) # available time spans for day/week/month
	# now we have a measurement every half hour
	spans = 2*spans
	
	data_span = []
	
	print span
	if span == 'day':
		print 'span', len(data)
		if len(data) >= spans[0]:
			data_span = (data[0:spans[0]])
	if span == 'week':
		if len(data) >= spans[1]:
			data_span = (data[0:spans[1]])
	if span == 'month':
		if len(data) >= spans[2]:
			data_span = (data[0:spans[2]])
	
	return data_span

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)

def plot_mult_in_one(data, span):
	data = select_data_span(data, span)
	data = np.array(data)
	data = np.flipud(data)
	t_str = [entry[0] for entry in data]
	#t_str = data[:,0]
	
	data = np.array([list(x[1:]) for x in data]) # remove timestamp
	#t = np.tile(t0, (len(data),1))
	
	float_arr = np.vectorize(float)
	data = float_arr(data)
	#int_arr = np.vectorize(int)
	t_hours_str = [timestamp[-8:-6] for timestamp in t_str]
	#if time.localtime().tm_isdst:
	#	time_shift = 2
	#else:
	#	time_shift = 1
	
	#t_hours_str = [int(entry)+time_shift for entry in t_hours_str] # TODO database logs in UTC, but we have CET
	#t_hours_str = [entry.split('.')[0] for entry in t_hours_str]
	# TODO set t to t_hours
	t = np.arange(len(data))
	#print(t_hours)

	fig, host = plt.subplots()
	fig.subplots_adjust(right=0.75)

	par1 = host.twinx()
	par2 = host.twinx()

	# Offset the right spine of par2.  The ticks and label have already been
	# placed on the right by twinx above.
	par2.spines["right"].set_position(("axes", 1.2))
	# Having been created by twinx, par2 has its frame off, so the line of its
	# detached spine is invisible.  First, activate the frame but make the patch
	# and spines invisible.
	make_patch_spines_invisible(par2)
	# Second, show the right spine.
	par2.spines["right"].set_visible(True)

	p1, = host.plot(t, data[:,0], "b-", label="Temp. (degree C)")
	p2, = par1.plot(t, data[:,1], "r-", label="Press. (hPa)")
	p3, = par2.plot(t, data[:,2], "g-", label="Humid. (% rel.)")

	#host.set_xlim(0, 2)
	#host.set_ylim(0, 2)
	#par1.set_ylim(0, 4)
	#par2.set_ylim(1, 65)

	host.set_xlabel("Time")
	host.set_ylabel("Temp.")
	par1.set_ylabel("Press.")
	par2.set_ylabel("Humid.")

	host.yaxis.label.set_color(p1.get_color())
	par1.yaxis.label.set_color(p2.get_color())
	par2.yaxis.label.set_color(p3.get_color())
	
	host.grid(which='both', color=[0.8, 0.8, 0.8], linestyle='-', linewidth=0.8)

	host.set_ylim(15,30)
	par1.set_ylim(950,970)
	par2.set_ylim(30,70)

	tkw = dict(size=4, width=1.5)
	host.tick_params(axis='y', colors=p1.get_color(), **tkw)
	par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
	par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
	host.tick_params(axis='x', **tkw)

	tick_skip = 4
	ticks = t[0::tick_skip]
	tick_labels = t_hours_str[0::tick_skip]
	host.set_xticks(ticks, minor=False)
	host.set_xticklabels(tick_labels, fontdict=None, minor=False)

	lines = [p1, p2, p3]

	host.legend(lines, [l.get_label() for l in lines])
	
	plt.savefig(TMP_FILENAME, bbox_inches='tight')


def plot_nicely(data, span):
	
	data = select_data_span(data, span)
	data = np.array(data)
	#t0 = data[:,0]
	data = data[:,1:] # remove timestamp
	#t = np.tile(t0, (len(data),1))
	
	float_arr = np.vectorize(float)
	data_num = float_arr(data)
	
	#print(t)
	#print('tttttttttttttttttttttttttttt')
	plt.plot(data_num)
	plt.title('Data collection for last ' + span)
	plt.xlabel('time')
	plt.ylabel('degree (C)')
	#plt.show()

	plt.savefig(TMP_FILENAME, bbox_inches='tight')
	
