from django.shortcuts import render
import mpld3, pylab as plt, numpy as np, pdb

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
    scatter = ax.scatter(b_objs.values_list(plot_type,flat=True),
                         b_objs.values_list('site_eui',flat=True))
    xlim=ax.get_xlim()
    ylim=ax.get_ylim()
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    med_eui = np.median(b_objs.values_list('site_eui',flat=True))
    ax.plot(xlim,[targ_eui,targ_eui],'k--',label='ASHRAE target')
    ax.plot(xlim,[med_eui,med_eui],'C0:',label='Median')
    ax.legend()
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
