from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('stock/<str:symbol>/', views.stock_detail, name='stock_detail'),
    path('portfolio/', views.portfolio, name='portfolio'),
    
    # API endpoints
    path('api/add-stock/', views.add_stock, name='add_stock'),
    path('api/add-to-portfolio/', views.add_to_portfolio, name='add_to_portfolio'),
    path('api/search-stocks/', views.search_stocks, name='search_stocks'),
    path('api/refresh-stock/', views.refresh_stock_data, name='refresh_stock'),
    path('api/market-overview/', views.market_overview, name='market_overview'),
]