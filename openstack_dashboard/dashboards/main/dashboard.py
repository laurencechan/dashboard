#-*- coding:utf-8 -*-

from django.utils.translation import ugettext_lazy as _

import horizon

class Main(horizon.Dashboard):
    name = _("Main")
    slug = "main"
    icon = ("img/menu_icon/menu_icon1.png")
    default_panel = 'main'


horizon.register(Main)