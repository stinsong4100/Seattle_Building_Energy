from django.shortcuts import render
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, mpld3, numpy as np, pdb

from .models import Building, ASHRAE_target
# Create your views here.

def index(request):
    try:
        b_use = request.POST['building_use']
        plot_type = request.POST['property']
    except:
        b_use = 'Office'
        plot_type = 'Year_remodeled'
    b_objs = Building.objects.filter(main_use=b_use)
    ash_targ = ASHRAE_target.objects.filter(main_use=b_use)
    targ_eui = ash_targ.values_list('target',flat=True)[0]

    f,ax=plt.subplots()
    f.subplots_adjust(left=0.15,bottom=0.12)
    matplotlib.rc('font',size=18)
    scatter = ax.scatter(b_objs.values_list(plot_type,flat=True),
                         b_objs.values_list('site_eui',flat=True))
    xlim=ax.get_xlim()
    ylim=ax.get_ylim()
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    med_eui = np.median(b_objs.values_list('site_eui',flat=True))
    ax.plot(xlim,[targ_eui,targ_eui],'k--',
            label='ASHRAE target: %.1f'%(targ_eui))
    ax.plot(xlim,[med_eui,med_eui],'C0:',label='Median: %.1f'%(med_eui))

    ax.set_xlabel(plot_type,fontsize=18)
    ax.set_ylabel('Energy Usage Intensity (EUI) [kBTU / sq ft / year]',fontsize=18)
    ax.tick_params(axis='both',which='major',labelsize=18)
    for tick in (ax.get_xticklabels()+ax.get_yticklabels()):
        tick.set_fontname('Times')

    ax.legend(loc=2)
    targets = ["http://blue.kingcounty.com/Assessor/eRealProperty/Detail.aspx?ParcelNbr="+f"{t:010}" for t in b_objs.values_list('Tax_PIN',flat=True)]
    tooltip = mpld3.plugins.PointHTMLTooltip(scatter,
                  labels=list(b_objs.values_list('Property_Name',flat=True)),
                  targets=targets)
    mpld3.plugins.connect(f,tooltip)
    js_plot = mpld3.fig_to_html(f)

    uses = Building.objects.values_list('main_use',flat=True).distinct()
    plot_types = [f.name for f in Building._meta.get_fields() if f.get_internal_type() is not 'CharField']
    context = {'js_plot': js_plot, 'building_uses':uses,
               'plots':plot_types,'selected_use':b_use,
               'selected_plot':plot_type}
    return render(request, 'plots/index.html', context)
