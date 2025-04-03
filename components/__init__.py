# components/__init__.py
"""
Modul komponen UI untuk aplikasi analisis server Rise of Kingdoms.
Berisi fungsi-fungsi untuk merender berbagai tab dan visualisasi.
"""

from components.overview import render_overview_tab
from components.time_analysis import render_time_analysis_tab
from components.map_analysis import render_map_analysis_tab
from components.predictions import render_prediction_tab
from components.dashboard import render_dashboard_header, render_stat_cards, render_server_growth_chart
from components.notification import render_notification_subscription, render_notification_settings

__all__ = [
    'render_overview_tab',
    'render_time_analysis_tab',
    'render_map_analysis_tab',
    'render_prediction_tab',
    'render_dashboard_header',
    'render_stat_cards',
    'render_server_growth_chart',
    'render_notification_subscription',
    'render_notification_settings'
]