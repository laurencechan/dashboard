from horizon import tables

from openstack_dashboard.dashboards.statistics.vm_run \
    import tables as project_tables

class MainIndexView(tables.DataTableView):
    table_class = project_tables.MainTable
    template_name = 'statistics/vm_run/main.html'
    page_title = "main page"

    def get_data(self):
        data = []
        return data