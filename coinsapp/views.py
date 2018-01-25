from django.shortcuts import render, render_to_response

from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.resources import CDN
from models import Coin, Value, Coinproperties
from django.http import Http404
from datetime import datetime, timedelta
import numpy as np
from numpy import convolve

def all_coindata(request):

    coin_list = Coin.objects.order_by('-coinproperties__coin_perchange')
    values = Value.objects.all()
    properties = Coinproperties.objects.order_by('coin_perchange')
    # value_list_recent= value_list_recent["coin_value"]
    context = {'coin_list': coin_list, 'properties':properties}
    return render(request, 'coinsapp/index.html', context)

def build_chart(request, coins_id):

    try:
        c = Coin.objects.get(id=coins_id)
        x=[]
        y=[]
        for values in c.value_set.all():
            x.append(values.reqtime)
            y.append(values.coin_value)
        # create a new plot with a title and axis labels


        def movingaverage (values, window):
            weights = np.repeat(1.0, window)/window
            sma = list(np.convolve(values, weights, 'valid'))

            n=0

            while (n < window-1):
                n=n+1
                nan = float('nan')
                sma.insert(0,nan)
            return sma

        sma = movingaverage (y, 5)
        p = figure(title=c.coin_name, x_axis_label='Time', y_axis_label='Price', x_axis_type='datetime', height=250)
        p.line( x,sma, legend="SMA", line_color="red", line_width=2 )
        p.toolbar.logo = None
        # add a line renderer with legend and line thickness
        p.line(x, y, legend=c.coin_name, line_width=2)
        p.circle(x, y, fill_color="white", size=8)
        p.sizing_mode = 'scale_width'
        script, div = components(p, CDN)


        x_h=[]
        y_h=[]
        t=datetime.now()-timedelta(minutes=60)
        for values in c.value_set.filter(reqtime__gt=t):
            x_h.append(values.reqtime)
            y_h.append(values.coin_value)

        sma_ = movingaverage (y, 5)
        p_h = figure(title=c.coin_name, x_axis_label='Time', y_axis_label='Price', x_axis_type='datetime', height=250)
        p_h.toolbar.logo = None
        # add a line renderer with legend and line thickness
        p_h.line(x_h, y_h, legend=c.coin_name, line_width=2)
        p_h.circle(x_h, y_h, fill_color="white", size=8)
        p_h.sizing_mode = 'scale_width'

        script_h, div_h = components(p_h)
        # output_file("lines.html")
        # show(p)


    except Value.DoesNotExist:
        raise Http404("Coin value does not exist")
    return render(request,'coinsapp/coin_chart.html',
        {'bk_script' : script , 'bk_div' : div, 'h_bk_script':script_h, 'h_bk_div':div_h} )