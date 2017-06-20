from django.utils.translation import ugettext_lazy as _

import horizon

class Main(horizon.Panel):
    name = _("Main")
    slug = 'main'
