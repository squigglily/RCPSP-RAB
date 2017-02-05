def main():
    from datetime import date
    from random import randint

    from bokeh.io import output_file, show, vform
    from bokeh.plotting import figure
    from bokeh.layouts import widgetbox
    from bokeh.models import ColumnDataSource, Range1d
    from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
    from bokeh.charts import Bar
    from bokeh.layouts import row
    import pandas as pd

    output_file("data_table.html")

    data = dict(
	        dates=[date(2014, 3, i+1) for i in range(10)],
	        downloads=[randint(0, 100) for i in range(10)],
	    )
    print(data)
    source = ColumnDataSource(data)

    columns = [
	        TableColumn(field="dates", title="Date", formatter=DateFormatter()),
	        TableColumn(field="downloads", title="Downloads"),
	    ]

    data_table = DataTable(source=source, columns=columns, width=400, height=280)
    bar = Bar(data, values = "downloads", label = "dates", plot_width = 400, tools = "tap")
    show(row(bar, widgetbox(data_table)))