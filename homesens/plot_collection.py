import matplotlib
matplotlib.use('Agg')  # run matplotlib headless (for virtualenv)
import matplotlib.pyplot as plt # now we can import pyplot also headless
import numpy as np
import time, os
import pickle

TMP_FILENAME_PREFIX = 'homesens/static/images/tmp_plot_collection'
TMP_FILENAME_EXT = '.png'


def select_data_span(data, span):
	
	spans = np.array([24, 24*7, 24*30, 24*365]) # available time spans for day/week/month/year
	# now we have a measurement every half hour
	spans = 2*spans
	
	data_span = []
	end_idx = None
	
	# print 'selected time span:', span
	if span == 'day':
		end_idx = spans[0]
	elif span == 'week':
		end_idx = spans[1]
	elif span == 'month':
		end_idx = spans[2]
	elif span == 'year':
		end_idx = spans[3]  
	
	if len(data) >= end_idx:
		data_span = (data[:end_idx])
	else:
		data_span = data
	
	return data_span


def make_patch_spines_invisible(ax):
	ax.set_frame_on(True)
	ax.patch.set_visible(False)
	for sp in ax.spines.values():
		sp.set_visible(False)

def plot_mult_in_one(data, span):
	data = select_data_span(data, span)
	data = np.array(data)
	data = np.flipud(data) # entries come in reversed order
	t_str = [entry[0] for entry in data]
	
	timestamps = [''.join(list(x[0])) for x in data]
	
	data = np.array([list(x[1:]) for x in data]) # remove timestamp
	
	float_arr = np.vectorize(float)
	data = float_arr(data)
	t_hours_str = [timestamp[-8:-6] for timestamp in t_str]
	#if time.localtime().tm_isdst:
	#   time_shift = 2
	#else:
	#   time_shift = 1

	t = np.arange(len(data))

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
	
	if span == 'year':
		# print("Smoothing data...")
		data_smoothed = np.zeros(data.shape)
		N = 2*24*14 # 2: twice per hour, 24 hours, 14 days = two week moving average: no of smoothing window samples
		data_smoothed = []
		for d in range(0, data.shape[1]):
			data_smoothed.append(np.convolve(data[:,d], np.ones((N,))/N, mode='valid'))
		# append start values before smoothed values to obtain same length again
		new_data = np.array(data_smoothed).T
		ext_data = np.repeat(new_data[0,:].reshape(1,-1), N-1, axis=0)
		data = np.vstack((ext_data, new_data))
		
		
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

	host.set_ylim(15,30) # temp
	par1.set_ylim(930,970) # press
	par2.set_ylim(30,80) # humid

	tkw = dict(size=4, width=1.5)
	host.tick_params(axis='y', colors=p1.get_color(), **tkw)
	par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
	par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
	host.tick_params(axis='x', **tkw)
	
	ticks = []
	tick_labels = []
	if span == 'day':
		ts = 2*2*1
		ticks = np.arange(0,len(data),ts,dtype=int)
		tick_labels = [entry[11:13] for entry in [timestamps[i] for i in ticks]]
	elif span == 'week':
		ts = 2*24
		ticks = np.arange(0,len(data),ts,dtype=int)
		tick_labels = [entry[:10] for entry in [timestamps[i] for i in ticks]]
	elif span == 'month':
		ts = 2*24*2
		ticks = np.arange(0,len(data),ts,dtype=int)
		tick_labels = [entry[:10] for entry in [timestamps[i] for i in ticks]]
	elif span == 'year':
		ts = 2*24*30
		ticks = np.arange(0,len(data),ts,dtype=int)
		tick_labels = [entry[:10] for entry in [timestamps[i] for i in ticks]]
	
	#print len(ticks), ticks
	#print len(data)
	#print len(timestamps)
	
	host.set_xticks(ticks)
	host.set_xticklabels(tick_labels, fontdict=None, rotation = 45)

	plt.xticks(rotation=70)

	lines = [p1, p2, p3]

	host.legend(lines, [l.get_label() for l in lines])
	
	filename = TMP_FILENAME_PREFIX + '_' + span + '_' + str(time.time()) + TMP_FILENAME_EXT
	os.system('touch ' + filename)
	os.system('chmod +777 ' + filename)
	plt.savefig(filename, bbox_inches='tight')


def plot_nicely(data, span):
	
	data = select_data_span(data, span)
	data = np.array(data)
	#t0 = data[:,0]
	data = data[:,1:] # remove timestamp
	#t = np.tile(t0, (len(data),1))
	
	float_arr = np.vectorize(float)
	data_num = float_arr(data)
	
	plt.plot(data_num)
	plt.title('Data collection for last ' + span)
	plt.xlabel('time')
	plt.ylabel('degree (C)')
	#plt.show()

	plt.savefig(TMP_FILENAME, bbox_inches='tight')
	
