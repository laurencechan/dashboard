from horizon import tables

class MainTable(tables.DataTable):
    column1 = tables.Column("column1", verbose_name="column1")
    class Meta(object):
        name = "maintable"
        verbose_name = "maintable"