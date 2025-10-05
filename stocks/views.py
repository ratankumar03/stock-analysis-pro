# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# from django.contrib import messages
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
# from django.db import transaction
# import json
# import plotly.graph_objs as go
# import plotly.offline as pyo
# from plotly.subplots import make_subplots
# import pandas as pd
# from datetime import datetime, timedelta
# from .database import StockDataService
# import logging

# logger = logging.getLogger(__name__)

# # Initialize the service
# stock_service = StockDataService()

# def dashboard(request):
#     """Main dashboard view with market overview"""
#     try:
#         # Get market summary
#         market_summary = stock_service.get_market_summary()
        
#         # Get top gainers and losers
#         gainers_losers = stock_service.get_top_gainers_losers()
        
#         # Get popular stocks (you can modify this list)
#         popular_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', 'NFLX']
#         stocks_data = []
        
#         for symbol in popular_symbols:
#             stock_info = stock_service.get_stock_info(symbol)
#             if not stock_info:
#                 # Fetch if not available
#                 stock_info = stock_service.fetch_stock_data(symbol, period="3mo")
            
#             if stock_info:
#                 stocks_data.append(stock_info)
        
#         # Pagination
#         paginator = Paginator(stocks_data, 6)  # Show 6 stocks per page
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
        
#         context = {
#             'stocks': page_obj,
#             'market_summary': market_summary,
#             'gainers': gainers_losers.get('gainers', [])[:3],
#             'losers': gainers_losers.get('losers', [])[:3],
#             'total_stocks': len(stocks_data)
#         }
        
#         return render(request, 'dashboard.html', context)
        
#     except Exception as e:
#         logger.error(f"Error loading dashboard: {str(e)}")
#         messages.error(request, f"Error loading dashboard: {str(e)}")
#         return render(request, 'dashboard.html', {
#             'stocks': [],
#             'market_summary': {},
#             'gainers': [],
#             'losers': [],
#             'total_stocks': 0
#         })

# def stock_detail(request, symbol):
#     """Stock detail view with comprehensive charts and analysis"""
#     try:
#         # Get or fetch stock data
#         stock_info = stock_service.get_stock_info(symbol)
#         if not stock_info:
#             stock_info = stock_service.fetch_stock_data(symbol, period="1y")
        
#         if not stock_info:
#             messages.error(request, f"Stock {symbol} not found")
#             return redirect('dashboard')
        
#         # Get price history for different periods
#         price_history_90 = stock_service.get_price_history(symbol, days=90)
#         price_history_30 = stock_service.get_price_history(symbol, days=30)
        
#         # Create comprehensive charts
#         charts_html = create_stock_charts(symbol, price_history_90, stock_info)
        
#         # Calculate technical indicators
#         technical_analysis = calculate_technical_indicators(price_history_30)
        
#         context = {
#             'stock': stock_info,
#             'charts': charts_html,
#             'technical_analysis': technical_analysis,
#             'price_history': price_history_30[-10:]  # Last 10 days for table
#         }
        
#         return render(request, 'stock_detail.html', context)
        
#     except Exception as e:
#         logger.error(f"Error loading stock details for {symbol}: {str(e)}")
#         messages.error(request, f"Error loading stock details: {str(e)}")
#         return redirect('dashboard')

# def create_stock_charts(symbol, price_history, stock_info):
#     """Create comprehensive stock charts"""
#     if not price_history:
#         return {"price_chart": "<div>No data available for charts</div>"}
    
#     # Prepare data
#     dates = [record['date'] for record in price_history]
#     opens = [record['open'] for record in price_history]
#     highs = [record['high'] for record in price_history]
#     lows = [record['low'] for record in price_history]
#     closes = [record['close'] for record in price_history]
#     volumes = [record['volume'] for record in price_history]
    
#     # Create subplots
#     fig = make_subplots(
#         rows=2, cols=1,
#         shared_xaxes=True,
#         vertical_spacing=0.1,
#         subplot_titles=(f'{symbol} Stock Price', 'Volume'),
#         row_width=[0.7, 0.3]
#     )
    
#     # Candlestick chart
#     candlestick = go.Candlestick(
#         x=dates,
#         open=opens,
#         high=highs,
#         low=lows,
#         close=closes,
#         name="Price",
#         increasing_line_color='green',
#         decreasing_line_color='red'
#     )
    
#     fig.add_trace(candlestick, row=1, col=1)
    
#     # Volume bar chart
#     volume_colors = ['green' if closes[i] > opens[i] else 'red' for i in range(len(closes))]
#     volume_trace = go.Bar(
#         x=dates,
#         y=volumes,
#         name='Volume',
#         marker=dict(color=volume_colors),
#         opacity=0.7
#     )
    
#     fig.add_trace(volume_trace, row=2, col=1)
    
#     # Update layout
#     fig.update_layout(
#         title=f'{stock_info["name"]} ({symbol}) - Stock Analysis',
#         xaxis_rangeslider_visible=False,
#         height=600,
#         showlegend=True,
#         template='plotly_white'
#     )
    
#     fig.update_xaxes(title_text="Date", row=2, col=1)
#     fig.update_yaxes(title_text="Price ($)", row=1, col=1)
#     fig.update_yaxes(title_text="Volume", row=2, col=1)
    
#     # Convert to HTML
#     chart_html = pyo.plot(fig, output_type='div', include_plotlyjs=False)
    
#     return {"price_chart": chart_html}

# def calculate_technical_indicators(price_history):
#     """Calculate basic technical indicators"""
#     if len(price_history) < 20:
#         return {}
    
#     df = pd.DataFrame(price_history)
    
#     # Simple Moving Averages
#     df['SMA_10'] = df['close'].rolling(window=10).mean()
#     df['SMA_20'] = df['close'].rolling(window=20).mean()
    
#     # RSI calculation
#     delta = df['close'].diff()
#     gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
#     loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
#     rs = gain / loss
#     rsi = 100 - (100 / (1 + rs))
    
#     latest_data = df.iloc[-1]
#     latest_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 0
    
#     return {
#         'sma_10': round(latest_data.get('SMA_10', 0), 2),
#         'sma_20': round(latest_data.get('SMA_20', 0), 2),
#         'rsi': round(latest_rsi, 2),
#         'current_price': round(latest_data['close'], 2)
#     }

# @login_required
# def portfolio(request):
#     """User portfolio view with detailed analysis"""
#     try:
#         portfolio_data = stock_service.calculate_portfolio_value(request.user.id)
        
#         # Create portfolio pie chart
#         if portfolio_data['portfolio_details']:
#             portfolio_chart = create_portfolio_chart(portfolio_data['portfolio_details'])
#         else:
#             portfolio_chart = "<div class='text-center'>No portfolio data available</div>"
        
#         context = {
#             'portfolio_summary': portfolio_data,
#             'portfolio_chart': portfolio_chart,
#             'portfolio_items': portfolio_data['portfolio_details']
#         }
        
#         return render(request, 'portfolio.html', context)
        
#     except Exception as e:
#         logger.error(f"Error loading portfolio: {str(e)}")
#         messages.error(request, f"Error loading portfolio: {str(e)}")
#         return render(request, 'portfolio.html', {
#             'portfolio_summary': {'total_value': 0, 'total_cost': 0, 'total_gain_loss': 0},
#             'portfolio_chart': '',
#             'portfolio_items': []
#         })

# def create_portfolio_chart(portfolio_details):
#     """Create portfolio allocation pie chart"""
#     if not portfolio_details:
#         return "<div>No portfolio data</div>"
    
#     symbols = [item['symbol'] for item in portfolio_details]
#     values = [item['current_value'] for item in portfolio_details]
    
#     fig = go.Figure(data=[go.Pie(
#         labels=symbols,
#         values=values,
#         hole=0.3,
#         textinfo='label+percent',
#         textposition='outside'
#     )])
    
#     fig.update_layout(
#         title="Portfolio Allocation",
#         height=400,
#         showlegend=True,
#         template='plotly_white'
#     )
    
#     return pyo.plot(fig, output_type='div', include_plotlyjs=False)

# @csrf_exempt
# def add_stock(request):
#     """Add new stock to tracking"""
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             symbol = data.get('symbol', '').upper().strip()
            
#             if not symbol:
#                 return JsonResponse({'error': 'Symbol is required'}, status=400)
            
#             # Check if stock already exists
#             existing_stock = stock_service.get_stock_info(symbol)
#             if existing_stock:
#                 return JsonResponse({
#                     'success': True,
#                     'message': f'Stock {symbol} already exists in database',
#                     'stock': existing_stock
#                 })
            
#             # Fetch new stock data
#             stock_info = stock_service.fetch_stock_data(symbol, period="6mo")
            
#             if stock_info:
#                 return JsonResponse({
#                     'success': True,
#                     'message': f'Stock {symbol} added successfully',
#                     'stock': stock_info
#                 })
#             else:
#                 return JsonResponse({
#                     'error': f'Could not fetch data for {symbol}. Please check the symbol.'
#                 }, status=400)
                
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON data'}, status=400)
#         except Exception as e:
#             logger.error(f"Error adding stock: {str(e)}")
#             return JsonResponse({'error': str(e)}, status=500)
    
#     return JsonResponse({'error': 'Invalid request method'}, status=405)

# @csrf_exempt
# @login_required
# def add_to_portfolio(request):
#     """Add stock to user portfolio"""
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             symbol = data.get('symbol', '').upper().strip()
#             quantity = float(data.get('quantity', 0))
#             purchase_price = float(data.get('purchase_price', 0))
            
#             if not all([symbol, quantity > 0, purchase_price > 0]):
#                 return JsonResponse({
#                     'error': 'Symbol, quantity, and purchase price are required'
#                 }, status=400)
            
#             # Verify stock exists
#             stock_info = stock_service.get_stock_info(symbol)
#             if not stock_info:
#                 return JsonResponse({
#                     'error': f'Stock {symbol} not found in database'
#                 }, status=400)
            
#             # Add to portfolio
#             success = stock_service.add_to_portfolio(
#                 request.user.id, symbol, quantity, purchase_price
#             )
            
#             if success:
#                 return JsonResponse({
#                     'success': True,
#                     'message': f'Added {quantity} shares of {symbol} to portfolio'
#                 })
#             else:
#                 return JsonResponse({'error': 'Failed to add to portfolio'}, status=500)
                
#         except (ValueError, TypeError) as e:
#             return JsonResponse({'error': 'Invalid numeric values'}, status=400)
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON data'}, status=400)
#         except Exception as e:
#             logger.error(f"Error adding to portfolio: {str(e)}")
#             return JsonResponse({'error': str(e)}, status=500)
    
#     return JsonResponse({'error': 'Invalid request method'}, status=405)

# def search_stocks(request):
#     """Search for stocks by symbol or name"""
#     query = request.GET.get('q', '').strip()
#     if len(query) < 1:
#         return JsonResponse({'stocks': []})
    
#     try:
#         # Search in database first
#         stocks = stock_service.search_stocks(query, limit=10)
        
#         # If no results and query looks like a symbol, try fetching
#         if not stocks and len(query) <= 5 and query.isalpha():
#             stock_info = stock_service.fetch_stock_data(query.upper())
#             if stock_info:
#                 stocks = [stock_info]
        
#         return JsonResponse({'stocks': stocks})
        
#     except Exception as e:
#         logger.error(f"Error searching stocks: {str(e)}")
#         return JsonResponse({'error': str(e)}, status=500)

# @csrf_exempt
# def refresh_stock_data(request):
#     """Refresh stock data for a specific symbol"""
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             symbol = data.get('symbol', '').upper().strip()
            
#             if not symbol:
#                 return JsonResponse({'error': 'Symbol is required'}, status=400)
            
#             # Fetch fresh data
#             stock_info = stock_service.fetch_stock_data(symbol, period="6mo")
            
#             if stock_info:
#                 return JsonResponse({
#                     'success': True,
#                     'message': f'Data refreshed for {symbol}',
#                     'stock': stock_info
#                 })
#             else:
#                 return JsonResponse({
#                     'error': f'Could not refresh data for {symbol}'
#                 }, status=400)
                
#         except Exception as e:
#             logger.error(f"Error refreshing stock data: {str(e)}")
#             return JsonResponse({'error': str(e)}, status=500)
    
#     return JsonResponse({'error': 'Invalid request method'}, status=405)

# def market_overview(request):
#     """Market overview API endpoint"""
#     try:
#         market_summary = stock_service.get_market_summary()
#         gainers_losers = stock_service.get_top_gainers_losers(limit=10)
        
#         return JsonResponse({
#             'market_summary': market_summary,
#             'top_gainers': gainers_losers.get('gainers', []),
#             'top_losers': gainers_losers.get('losers', [])
#         })
        
#     except Exception as e:
#         logger.error(f"Error getting market overview: {str(e)}")
#         return JsonResponse({'error': str(e)}, status=500)


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
import json
import plotly.graph_objs as go
import plotly.offline as pyo
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from .database import StockDataService
import logging

logger = logging.getLogger(__name__)

# Initialize the service
stock_service = StockDataService()

def dashboard(request):
    """Main dashboard view with market overview"""
    try:
        # Get market summary
        market_summary = stock_service.get_market_summary()
        
        # Get top gainers and losers
        gainers_losers = stock_service.get_top_gainers_losers()
        
        # Get popular stocks (you can modify this list)
        popular_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', 'NFLX']
        stocks_data = []
        
        for symbol in popular_symbols:
            stock_info = stock_service.get_stock_info(symbol)
            if not stock_info:
                # Fetch if not available
                stock_info = stock_service.fetch_stock_data(symbol, period="3mo")
            
            if stock_info:
                stocks_data.append(stock_info)
        
        # Pagination
        paginator = Paginator(stocks_data, 6)  # Show 6 stocks per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'stocks': page_obj,
            'market_summary': market_summary,
            'gainers': gainers_losers.get('gainers', [])[:3],
            'losers': gainers_losers.get('losers', [])[:3],
            'total_stocks': len(stocks_data)
        }
        
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return render(request, 'dashboard.html', {
            'stocks': [],
            'market_summary': {},
            'gainers': [],
            'losers': [],
            'total_stocks': 0
        })

def stock_detail(request, symbol):
    """Stock detail view with comprehensive charts and analysis"""
    try:
        # Get or fetch stock data
        stock_info = stock_service.get_stock_info(symbol)
        if not stock_info:
            stock_info = stock_service.fetch_stock_data(symbol, period="1y")
        
        if not stock_info:
            messages.error(request, f"Stock {symbol} not found")
            return redirect('dashboard')
        
        # Get price history for different periods
        price_history_90 = stock_service.get_price_history(symbol, days=90)
        price_history_30 = stock_service.get_price_history(symbol, days=30)
        
        # Create comprehensive charts
        charts_html = create_stock_charts(symbol, price_history_90, stock_info)
        
        # Calculate technical indicators
        technical_analysis = calculate_technical_indicators(price_history_30)
        
        context = {
            'stock': stock_info,
            'charts': charts_html,
            'technical_analysis': technical_analysis,
            'price_history': price_history_30[-10:]  # Last 10 days for table
        }
        
        return render(request, 'stock_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error loading stock details for {symbol}: {str(e)}")
        messages.error(request, f"Error loading stock details: {str(e)}")
        return redirect('dashboard')

def create_stock_charts(symbol, price_history, stock_info):
    """Create comprehensive stock charts"""
    if not price_history:
        return {"price_chart": "<div>No data available for charts</div>"}
    
    # Prepare data
    dates = [record['date'] for record in price_history]
    opens = [record['open'] for record in price_history]
    highs = [record['high'] for record in price_history]
    lows = [record['low'] for record in price_history]
    closes = [record['close'] for record in price_history]
    volumes = [record['volume'] for record in price_history]
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=(f'{symbol} Stock Price', 'Volume'),
        row_width=[0.7, 0.3]
    )
    
    # Candlestick chart
    candlestick = go.Candlestick(
        x=dates,
        open=opens,
        high=highs,
        low=lows,
        close=closes,
        name="Price",
        increasing_line_color='green',
        decreasing_line_color='red'
    )
    
    fig.add_trace(candlestick, row=1, col=1)
    
    # Volume bar chart
    volume_colors = ['green' if closes[i] > opens[i] else 'red' for i in range(len(closes))]
    volume_trace = go.Bar(
        x=dates,
        y=volumes,
        name='Volume',
        marker=dict(color=volume_colors),
        opacity=0.7
    )
    
    fig.add_trace(volume_trace, row=2, col=1)
    
    # Update layout
    fig.update_layout(
        title=f'{stock_info["name"]} ({symbol}) - Stock Analysis',
        xaxis_rangeslider_visible=False,
        height=600,
        showlegend=True,
        template='plotly_white'
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    # Convert to HTML
    chart_html = pyo.plot(fig, output_type='div', include_plotlyjs=False)
    
    return {"price_chart": chart_html}

def calculate_technical_indicators(price_history):
    """Calculate basic technical indicators"""
    if len(price_history) < 20:
        return {}
    
    df = pd.DataFrame(price_history)
    
    # Simple Moving Averages
    df['SMA_10'] = df['close'].rolling(window=10).mean()
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    
    # RSI calculation
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    latest_data = df.iloc[-1]
    latest_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 0
    
    return {
        'sma_10': round(latest_data.get('SMA_10', 0), 2),
        'sma_20': round(latest_data.get('SMA_20', 0), 2),
        'rsi': round(latest_rsi, 2),
        'current_price': round(latest_data['close'], 2)
    }

@login_required
def portfolio(request):
    """User portfolio view with detailed analysis"""
    try:
        portfolio_data = stock_service.calculate_portfolio_value(request.user.id)
        
        # Create portfolio pie chart
        if portfolio_data['portfolio_details']:
            portfolio_chart = create_portfolio_chart(portfolio_data['portfolio_details'])
        else:
            portfolio_chart = "<div class='text-center'>No portfolio data available</div>"
        
        context = {
            'portfolio_summary': portfolio_data,
            'portfolio_chart': portfolio_chart,
            'portfolio_items': portfolio_data['portfolio_details']
        }
        
        return render(request, 'portfolio.html', context)
        
    except Exception as e:
        logger.error(f"Error loading portfolio: {str(e)}")
        messages.error(request, f"Error loading portfolio: {str(e)}")
        return render(request, 'portfolio.html', {
            'portfolio_summary': {'total_value': 0, 'total_cost': 0, 'total_gain_loss': 0},
            'portfolio_chart': '',
            'portfolio_items': []
        })

def create_portfolio_chart(portfolio_details):
    """Create portfolio allocation pie chart"""
    if not portfolio_details:
        return "<div>No portfolio data</div>"
    
    symbols = [item['symbol'] for item in portfolio_details]
    values = [item['current_value'] for item in portfolio_details]
    
    fig = go.Figure(data=[go.Pie(
        labels=symbols,
        values=values,
        hole=0.3,
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Portfolio Allocation",
        height=400,
        showlegend=True,
        template='plotly_white'
    )
    
    return pyo.plot(fig, output_type='div', include_plotlyjs=False)

@require_http_methods(["POST"])
def add_stock(request):
    """Add new stock to tracking"""
    try:
        # Parse JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        # Validate symbol
        symbol = data.get('symbol', '').upper().strip()
        
        if not symbol:
            logger.error("No symbol provided")
            return JsonResponse({'error': 'Symbol is required'}, status=400)
        
        if len(symbol) > 10 or not symbol.replace('.', '').isalnum():
            logger.error(f"Invalid symbol format: {symbol}")
            return JsonResponse({'error': 'Invalid symbol format'}, status=400)
        
        logger.info(f"Attempting to add stock: {symbol}")
        
        # Check if stock already exists
        existing_stock = stock_service.get_stock_info(symbol)
        if existing_stock:
            logger.info(f"Stock {symbol} already exists")
            return JsonResponse({
                'success': True,
                'message': f'Stock {symbol} already exists in database',
                'stock': existing_stock
            })
        
        # For now, use demo data due to Yahoo Finance rate limits
        logger.info(f"Creating demo data for {symbol} due to rate limits")
        
        # Create demo data
        stock_info = stock_service.create_demo_stock_data(symbol)
        
        # Store demo data in database
        stock_service.stocks_collection.update_one(
            {"symbol": symbol.upper()},
            {"$set": stock_info},
            upsert=True
        )
        
        # Create demo price history
        stock_service._create_demo_price_history(symbol, stock_info['current_price'])
        
        if stock_info:
            logger.info(f"Successfully added stock: {symbol}")
            return JsonResponse({
                'success': True,
                'message': f'Stock {symbol} added successfully',
                'stock': stock_info
            })
        else:
            logger.error(f"Could not fetch data for symbol: {symbol}")
            return JsonResponse({
                'error': f'Could not fetch data for {symbol}. Please check the symbol and try again.'
            }, status=400)
            
    except Exception as e:
        logger.error(f"Error adding stock: {str(e)}")
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

@require_http_methods(["POST"])
@login_required
def add_to_portfolio(request):
    """Add stock to user portfolio"""
    try:
        # Parse JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        # Validate input data
        symbol = data.get('symbol', '').upper().strip()
        quantity = data.get('quantity', 0)
        purchase_price = data.get('purchase_price', 0)
        
        # Convert to float and validate
        try:
            quantity = float(quantity)
            purchase_price = float(purchase_price)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid numeric values'}, status=400)
        
        if not all([symbol, quantity > 0, purchase_price > 0]):
            return JsonResponse({
                'error': 'Symbol, quantity (>0), and purchase price (>0) are required'
            }, status=400)
        
        # Verify stock exists
        stock_info = stock_service.get_stock_info(symbol)
        if not stock_info:
            return JsonResponse({
                'error': f'Stock {symbol} not found in database. Please add it first.'
            }, status=400)
        
        # Add to portfolio
        success = stock_service.add_to_portfolio(
            request.user.id, symbol, quantity, purchase_price
        )
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Added {quantity} shares of {symbol} to portfolio'
            })
        else:
            return JsonResponse({'error': 'Failed to add to portfolio'}, status=500)
            
    except Exception as e:
        logger.error(f"Error adding to portfolio: {str(e)}")
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

def search_stocks(request):
    """Search for stocks by symbol or name"""
    query = request.GET.get('q', '').strip()
    if len(query) < 1:
        return JsonResponse({'stocks': []})
    
    try:
        # Search in database first
        stocks = stock_service.search_stocks(query, limit=10)
        
        # If no results and query looks like a symbol, try fetching
        if not stocks and len(query) <= 5 and query.isalpha():
            stock_info = stock_service.fetch_stock_data(query.upper())
            if stock_info:
                stocks = [stock_info]
        
        return JsonResponse({'stocks': stocks})
        
    except Exception as e:
        logger.error(f"Error searching stocks: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def refresh_stock_data(request):
    """Refresh stock data for a specific symbol"""
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        symbol = data.get('symbol', '').upper().strip()
        
        if not symbol:
            return JsonResponse({'error': 'Symbol is required'}, status=400)
        
        # Fetch fresh data
        stock_info = stock_service.fetch_stock_data(symbol, period="6mo")
        
        if stock_info:
            return JsonResponse({
                'success': True,
                'message': f'Data refreshed for {symbol}',
                'stock': stock_info
            })
        else:
            return JsonResponse({
                'error': f'Could not refresh data for {symbol}'
            }, status=400)
            
    except Exception as e:
        logger.error(f"Error refreshing stock data: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def market_overview(request):
    """Market overview API endpoint"""
    try:
        market_summary = stock_service.get_market_summary()
        gainers_losers = stock_service.get_top_gainers_losers(limit=10)
        
        return JsonResponse({
            'market_summary': market_summary,
            'top_gainers': gainers_losers.get('gainers', []),
            'top_losers': gainers_losers.get('losers', [])
        })
        
    except Exception as e:
        logger.error(f"Error getting market overview: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)