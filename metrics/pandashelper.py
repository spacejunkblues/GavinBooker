import matplotlib.pyplot as plt
import io
import urllib, base64
from datetime import datetime
from dateutil.relativedelta import relativedelta

def ConvertMonthtoName(month):
    #setup month name coverter
    month_converter={1:'January', 2:'February', 3:'March', 4:'April',\
                            5:'May', 6:'June', 7:'July', 8:'August',\
                            9:'September', 10:'October', 11:'November', 12:'December'}
    return month_converter[month]

#loads info for into the metricbar
#pass current page to enable next and previous
def GetBarData(page, year, month):

    #get current & next month
    if month == '':
        month=datetime.now().month
    if year == '':
        year=datetime.now().year
    
    #get next month
    next_date = datetime(year,month,1)+relativedelta(months=1)
    next_year = next_date.year
    next_month = next_date.month
    
    #get previous month
    prev_date = datetime(year,month,1)-relativedelta(months=1)
    previous_year = prev_date.year
    previous_month = prev_date.month
    
    #build metricbar data
    bar={'page':page,'year':year,'month':month,'monthName':ConvertMonthtoName(month),
        'next_year':next_year,'next_month':next_month,
        'previous_year':previous_year,'previous_month':previous_month}
    
    return bar

def buildgraph(ax, xlabel = None, ylabel = None, title=None):
    #format labels
    if xlabel != None:
        ax.set_xlabel(xlabel)
    if ylabel != None:
        ax.set_xlabel(ylabel)
    if title != None:
        ax.set_title(title)
    
    #get the figure
    fig = plt.gcf()
    
    #this will make so that the labels don't get cut off
    plt.tight_layout()
    
    #save the image to make it readable as an image in html
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    
    #clear the plot
    plt.clf()
    
    return urllib.parse.quote(string)