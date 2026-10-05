"""Componentes del framework UI ncurses."""
from ncurses_ui.components.button import Button
from ncurses_ui.components.checkbox import Checkbox
from ncurses_ui.components.composite import CardView, Composite, Dashboard, DataFull, FormView, ListView, MasterDetail
from ncurses_ui.components.containers import (
    AbsLayout,
    Accordion,
    Align,
    GridLayout,
    HeaderLayout,
    Portlet,
    Proxy,
    ScrollView,
)
from ncurses_ui.components.counter import Counter
from ncurses_ui.components.datatable import DataTable
from ncurses_ui.components.dataview import DataView
from ncurses_ui.components.form import Form
from ncurses_ui.components.grouplist import GroupList
from ncurses_ui.components.icon import Icon
from ncurses_ui.components.label import Label
from ncurses_ui.components.layout import Layout
from ncurses_ui.components.list import List
from ncurses_ui.components.navigation import ContextMenu, Hint, MainBar, Menu, Sidebar, Toolbar
from ncurses_ui.components.overlays import Context, Popup, Tooltip, Window
from ncurses_ui.components.pager import Pager
from ncurses_ui.components.property import Property
from ncurses_ui.components.radio import Radio
from ncurses_ui.components.rangeslider import RangeSlider
from ncurses_ui.components.search import Search
from ncurses_ui.components.screen import Screen
from ncurses_ui.components.selects import Combo, RichSelect, Select, Suggest
from ncurses_ui.components.slider import Slider
from ncurses_ui.components.spacer import Spacer
from ncurses_ui.components.tabs import Carousel, MultiView, TabBar, TabView
from ncurses_ui.components.template import Template
from ncurses_ui.components.text import Text
from ncurses_ui.components.textarea import Textarea
from ncurses_ui.components.timeline import TimeLine
from ncurses_ui.components.toggle import Toggle
from ncurses_ui.components.tree import Tree
from ncurses_ui.components.unitlist import UnitList
from ncurses_ui.components.viz import Bullet, Card, Chart, Gage


def register_defaults(registry):
    """Registra los componentes built-in en el ViewRegistry."""
    registry.register("datatable", DataTable)
    registry.register("template", Template)
    registry.register("label", Label)
    registry.register("spacer", Spacer)
    registry.register("icon", Icon)
    registry.register("button", Button)
    registry.register("text", Text)
    registry.register("textarea", Textarea)
    registry.register("search", Search)
    registry.register("checkbox", Checkbox)
    registry.register("radio", Radio)
    registry.register("toggle", Toggle)
    registry.register("switch", Toggle)
    registry.register("counter", Counter)
    registry.register("slider", Slider)
    registry.register("rangeslider", RangeSlider)
    registry.register("list", List)
    registry.register("property", Property)
    registry.register("grouplist", GroupList)
    registry.register("dataview", DataView)
    registry.register("unitlist", UnitList)
    registry.register("timeline", TimeLine)
    registry.register("tree", Tree)
    registry.register("pager", Pager)
    registry.register("layout", Layout)
    registry.register("screen", Screen)
    registry.register("window", Window)
    registry.register("popup", Popup)
    registry.register("tooltip", Tooltip)
    registry.register("context", Context)
    registry.register("multiview", MultiView)
    registry.register("carousel", Carousel)
    registry.register("tabbar", TabBar)
    registry.register("tabview", TabView)
    registry.register("proxy", Proxy)
    registry.register("scrollview", ScrollView)
    registry.register("align", Align)
    registry.register("abslayout", AbsLayout)
    registry.register("gridlayout", GridLayout)
    registry.register("headerlayout", HeaderLayout)
    registry.register("portlet", Portlet)
    registry.register("dashboard", Dashboard)
    registry.register("accordion", Accordion)
    registry.register("select", Select)
    registry.register("richselect", RichSelect)
    registry.register("combo", Combo)
    registry.register("suggest", Suggest)
    registry.register("menu", Menu)
    registry.register("contextmenu", ContextMenu)
    registry.register("sidebar", Sidebar)
    registry.register("toolbar", Toolbar)
    registry.register("mainbar", MainBar)
    registry.register("hint", Hint)
    registry.register("form", Form)
    registry.register("composite", Composite)
    registry.register("listview", ListView)
    registry.register("formview", FormView)
    registry.register("datafull", DataFull)
    registry.register("cardview", CardView)
    registry.register("masterdetail", MasterDetail)
    registry.register("gage", Gage)
    registry.register("card", Card)
    registry.register("bullet", Bullet)
    registry.register("chart", Chart)
