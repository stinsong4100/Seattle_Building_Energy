from django.shortcuts import render
import matplotlib
#matplotlib.use("Agg")
import matplotlib.pyplot as plt, mpld3, numpy as np, pdb
import matplotlib.colors as colors

from .models import Building, ASHRAE_target, Lookup
# Create your views here.

# From Joe Kington: This one gives two different linear ramps:
class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

def index(request):
    try:
        b_use = request.POST['building_use']
        plot_type = request.POST['property']
    except:
        b_use = 'Office'
        plot_type = 'Year_remodeled'
    b_objs = Building.objects.filter(main_use=b_use)
    b_euis=np.array(b_objs.values_list('site_eui',flat=True))
    plot_type_values = b_objs.values_list(plot_type,flat=True)

    ash_targ = ASHRAE_target.objects.filter(main_use=b_use)
    targ_eui = ash_targ.values_list('target',flat=True)[0]
    med_eui = np.median(b_euis)
    labels=["<p style='background-color:white'>"+
            '<br>'.join([n.title(),f'GFA: {a:.0f}',f'EUI: {eui:.1f}'])+'</p>' 
            for n,a,eui in b_objs.values_list('Property_Name',
                                      'No_parking_gfa','site_eui')]

    f,ax=plt.subplots()
    f.subplots_adjust(left=0.15,bottom=0.12)
    matplotlib.rc('font',size=18)
    the_cm = plt.get_cmap('plasma')
    if plot_type=='site_eui':
        # make histogram
        hist_max=np.min([np.max(b_euis),5*med_eui])
        ax.hist(b_euis,bins=20,range=[0,hist_max])
    else:
        scatter = ax.scatter(plot_type_values,b_euis,c=b_euis,cmap=the_cm,
                             norm=MidpointNormalize(midpoint=med_eui))

    xlim=ax.get_xlim()
    ylim=ax.get_ylim()
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    if plot_type=='site_eui':
        # target and median EUI lines are vertical in this case
        ax.plot([targ_eui,targ_eui],ylim,'k--',
                label='ASHRAE target: %.1f'%(targ_eui))
        ax.plot([med_eui,med_eui],ylim,'C1:',label='Median: %.1f'%(med_eui))
        ax.legend(loc=1)
    else:
        # make scatter plot clickable and have labels
        targets = ["http://blue.kingcounty.com/Assessor/eRealProperty/Detail.aspx?ParcelNbr="+f"{t:010}" for t in b_objs.values_list('Tax_PIN',flat=True)]
        tooltip = mpld3.plugins.PointHTMLTooltip(scatter,labels,
                                                 targets=targets)
        mpld3.plugins.connect(f,tooltip)
        ax.plot(xlim,[targ_eui,targ_eui],'k--',
                label='ASHRAE target: %.1f'%(targ_eui))
        ax.plot(xlim,[med_eui,med_eui],'C0:',label='Median: %.1f'%(med_eui))
        ax.set_ylabel('Energy Usage Intensity (EUI) [kBTU / sq ft / year]',fontsize=18)
        ax.legend(loc=2)


    if plot_type in Lookup.objects.values_list('case',flat=True).distinct():
        # print text for x labels
        case_objs=Lookup.objects.filter(case=plot_type)
        plt.xticks(case_objs.values_list('code',flat=True),
                   case_objs.values_list('value',flat=True))

    ax.set_xlabel(plot_type,fontsize=18)
    ax.tick_params(axis='both',which='major',labelsize=18)

    js_plot = mpld3.fig_to_html(f)

    uses = Building.objects.values_list('main_use',flat=True).distinct()
    plot_types = [f.name for f in Building._meta.get_fields() if f.get_internal_type() is not 'CharField']
    latlon = b_objs.values_list('lat','longitude')

    mn = MidpointNormalize(vmin=np.min(b_euis),vmax=np.max(b_euis),
                           midpoint=np.median(b_euis))
    orig_c = the_cm(mn(b_euis))
    colors = (orig_c[:,:3]*256).astype(int)
    colors = map(tuple, colors)

    context = {'js_plot': js_plot, 'building_uses':uses,
               'plots':plot_types,'selected_use':b_use, 'colors':colors,
               'selected_plot':plot_type, 'latlon':latlon}
    return render(request, 'plots/index.html', context)
