from horizon import tables

from openstack_dashboard.dashboards.storage.storages \
    import tables as project_tables

class MainIndexView(tables.DataTableView):
    table_class = project_tables.MainTable
    template_name = 'storage/storages/main.html'
    page_title = "main page"

    def get_data(self):
        data = []
        return data