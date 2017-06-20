#-*- coding:utf-8 -*-

from django.utils.translation import ugettext_lazy as _

import horizon

class Computeproject(horizon.Dashboard):
    name = _("ComputeMan")
    slug = "compute"
    icon = ("img/menu_icon/menu_icon2.png")
    default_panel = 'aggregates'

horizon.register(Computeproject)