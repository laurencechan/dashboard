# The slug of the panel to be added to HORIZON_CONFIG. Required.
PANEL = 'vm_run'
# The slug of the dashboard the PANEL associated with. Required.
PANEL_DASHBOARD = 'statistics'
# The slug of the panel group the PANEL is associated with.
PANEL_GROUP = 'default'

# Python panel class of the PANEL to be added.
ADD_PANEL = ('openstack_dashboard.dashboards.statistics.vm_run.panel.VM_run')
