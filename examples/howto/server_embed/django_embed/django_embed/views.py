from os.path import join
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.conf import settings
from django.shortcuts import render

from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.document import Document
from bokeh.themes import Theme
from bokeh.embed import server_document

from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature

def sea_surface_handler1(doc: Document) -> None:
    df = sea_surface_temperature.copy()
    source = ColumnDataSource(data=df)

    plot = figure(x_axis_type="datetime", y_range=(0, 25), y_axis_label="Temperature (Celsius)",
                  title="Sea Surface Temperature at 43.18, -70.43")
    plot.line("time", "temperature", source=source)

    def callback(attr: str, old: Any, new: Any) -> None:
        if new == 0:
            data = df
        else:
            data = df.rolling("{0}D".format(new)).mean()
        source.data = ColumnDataSource(data=data).data

    slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
    slider.on_change("value", callback)

    doc.add_root(column(slider, plot))

    doc.theme = Theme(filename=join(settings.THEMES_DIR, "theme.yaml"))

def sea_surface_handler2(doc: Document) -> None:
    sea_surface_handler1(doc)
    doc.template = """
{% block preamble %}
<style>
</style>
{% endblock %}
{% block contents %}
    <div>
    This Bokeh app below is served by a Django server:
    </div>
    {{ super() }}
{% endblock %}
    """

def sea_surface(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "embed.html", dict(script=script))