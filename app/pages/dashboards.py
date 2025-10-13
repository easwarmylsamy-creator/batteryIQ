from app.dashboards.admin import render_admin_dashboard
from app.dashboards.scientist import render_scientist_dashboard
from app.dashboards.client import client_dashboard
from app.dashboards.guest import render_guest_dashboard
from app.dashboards.super_admin import render_super_admin_dashboard

def admin_dashboard():
    render_admin_dashboard()

def scientist_dashboard():
    render_scientist_dashboard()

def clientDashboard():
    client_dashboard()


def guest_dashboard():
    render_guest_dashboard()

def super_admin_dashboard():
    render_super_admin_dashboard()