from pymongo import MongoClient
from django.conf import settings
import logging
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class MongoDBConnection:
    """Singleton MongoDB connection class"""
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            try:
                self._client = MongoClient(
                    settings.MONGODB_SETTINGS['URI'],
                    serverSelectionTimeoutMS=5000
                )
                self._db = self._client[settings.MONGODB_SETTINGS['DATABASE_NAME']]
                # Test connection
                self._client.admin.command('ping')
                logger.info("Successfully connected to MongoDB")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise ConnectionError(f"MongoDB connection failed: {e}")
    
    @property
    def db(self):
        return self._db
    
    @property
    def client(self):
        return self._client
    
    def close_connection(self):
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")

class StockDataService:
    """Service class for all stock-related database operations"""
    
    def __init__(self):
        self.mongo = MongoDBConnection()
        self.db = self.mongo.db
        self.stocks_collection = self.db.stocks
        self.portfolio_collection = self.db.portfolio
        self.price_history_collection = self.db.price_history
        self.watchlist_collection = self.db.watchlist
        
        # Create indexes for better performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create MongoDB indexes for better query performance"""
        try:
            self.stocks_collection.create_index("symbol", unique=True)
            self.price_history_collection.create_index([("symbol", 1), ("date", -1)])
            self.portfolio_collection.create_index([("user_id", 1), ("symbol", 1)])
            self.watchlist_collection.create_index([("user_id", 1), ("symbol", 1)])
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")
    
    def fetch_stock_data(self, symbol, period="1y"):
        """Fetch stock data from Yahoo Finance and store in MongoDB"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            
            if hist.empty:
                logger.warning(f"No data found for symbol: {symbol}")
                return None
                
            info = stock.info
            
            # Calculate additional metrics
            current_price = float(hist['Close'][-1])
            prev_close = float(hist['Close'][-2]) if len(hist) > 1 else current_price
            price_change = current_price - prev_close
            price_change_percent = (price_change / prev_close * 100) if prev_close != 0 else 0
            
            # Prepare stock data
            stock_data = {
                "symbol": symbol.upper(),
                "name": info.get('longName', symbol),
                "sector": info.get('sector', 'Unknown'),
                "industry": info.get('industry', 'Unknown'),
                "current_price": current_price,
                "previous_close": prev_close,
                "price_change": price_change,
                "price_change_percent": price_change_percent,
                "market_cap": info.get('marketCap', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "dividend_yield": info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                "52_week_high": info.get('fiftyTwoWeekHigh', 0),
                "52_week_low": info.get('fiftyTwoWeekLow', 0),
                "volume": int(hist['Volume'][-1]),
                "avg_volume": int(info.get('averageVolume', 0)),
                "beta": info.get('beta', 0),
                "eps": info.get('trailingEps', 0),
                "book_value": info.get('bookValue', 0),
                "last_updated": datetime.now()
            }
            
            # Update or insert stock data
            self.stocks_collection.update_one(
                {"symbol": symbol.upper()},
                {"$set": stock_data},
                upsert=True
            )
            
            # Store price history
            self._store_price_history(symbol, hist)
            
            logger.info(f"Successfully fetched and stored data for {symbol}")
            return stock_data
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    def _store_price_history(self, symbol, hist):
        """Store price history data"""
        try:
            price_data = []
            for date, row in hist.iterrows():
                if pd.isna(row).any():
                    continue
                    
                price_record = {
                    "symbol": symbol.upper(),
                    "date": date.to_pydatetime(),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume']) if not pd.isna(row['Volume']) else 0
                }
                price_data.append(price_record)
            
            if price_data:
                # Remove old price history and insert new
                self.price_history_collection.delete_many({"symbol": symbol.upper()})
                self.price_history_collection.insert_many(price_data)
                
        except Exception as e:
            logger.error(f"Error storing price history for {symbol}: {e}")
    
    def get_stock_info(self, symbol):
        """Get stock information from MongoDB"""
        try:
            return self.stocks_collection.find_one({"symbol": symbol.upper()})
        except Exception as e:
            logger.error(f"Error getting stock info for {symbol}: {e}")
            return None
    
    def get_all_stocks(self, limit=50):
        """Get all stocks from MongoDB with limit"""
        try:
            return list(self.stocks_collection.find().limit(limit))
        except Exception as e:
            logger.error(f"Error getting all stocks: {e}")
            return []
    
    def get_price_history(self, symbol, days=30):
        """Get price history for a stock"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            return list(self.price_history_collection.find({
                "symbol": symbol.upper(),
                "date": {"$gte": start_date}
            }).sort("date", 1))
        except Exception as e:
            logger.error(f"Error getting price history for {symbol}: {e}")
            return []
    
    def add_to_portfolio(self, user_id, symbol, quantity, purchase_price):
        """Add stock to user portfolio"""
        try:
            # Check if stock already exists in portfolio
            existing = self.portfolio_collection.find_one({
                "user_id": user_id,
                "symbol": symbol.upper()
            })
            
            if existing:
                # Update existing position
                new_quantity = existing['quantity'] + quantity
                new_avg_price = (
                    (existing['quantity'] * existing['purchase_price'] + 
                     quantity * purchase_price) / new_quantity
                )
                
                self.portfolio_collection.update_one(
                    {"_id": existing["_id"]},
                    {
                        "$set": {
                            "quantity": new_quantity,
                            "purchase_price": new_avg_price,
                            "last_updated": datetime.now()
                        }
                    }
                )
            else:
                # Create new position
                portfolio_item = {
                    "user_id": user_id,
                    "symbol": symbol.upper(),
                    "quantity": quantity,
                    "purchase_price": purchase_price,
                    "purchase_date": datetime.now(),
                    "last_updated": datetime.now()
                }
                self.portfolio_collection.insert_one(portfolio_item)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding to portfolio: {e}")
            return False
    
    def get_user_portfolio(self, user_id):
        """Get user's portfolio"""
        try:
            return list(self.portfolio_collection.find({"user_id": user_id}))
        except Exception as e:
            logger.error(f"Error getting portfolio for user {user_id}: {e}")
            return []
    
    def calculate_portfolio_value(self, user_id):
        """Calculate total portfolio value with detailed metrics"""
        try:
            portfolio = self.get_user_portfolio(user_id)
            
            total_value = 0
            total_cost = 0
            total_gain_loss = 0
            
            portfolio_details = []
            
            for item in portfolio:
                stock_info = self.get_stock_info(item['symbol'])
                if stock_info:
                    current_value = item['quantity'] * stock_info['current_price']
                    cost = item['quantity'] * item['purchase_price']
                    gain_loss = current_value - cost
                    gain_loss_percent = (gain_loss / cost * 100) if cost > 0 else 0
                    
                    total_value += current_value
                    total_cost += cost
                    total_gain_loss += gain_loss
                    
                    portfolio_details.append({
                        'symbol': item['symbol'],
                        'quantity': item['quantity'],
                        'purchase_price': item['purchase_price'],
                        'current_price': stock_info['current_price'],
                        'current_value': current_value,
                        'cost': cost,
                        'gain_loss': gain_loss,
                        'gain_loss_percent': gain_loss_percent
                    })
            
            total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
            
            return {
                "total_value": total_value,
                "total_cost": total_cost,
                "total_gain_loss": total_gain_loss,
                "total_gain_loss_percent": total_gain_loss_percent,
                "portfolio_details": portfolio_details
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio value: {e}")
            return {
                "total_value": 0,
                "total_cost": 0,
                "total_gain_loss": 0,
                "total_gain_loss_percent": 0,
                "portfolio_details": []
            }
    
    def search_stocks(self, query, limit=10):
        """Search for stocks by symbol or name"""
        try:
            # Search by symbol or name (case insensitive)
            search_query = {
                "$or": [
                    {"symbol": {"$regex": query, "$options": "i"}},
                    {"name": {"$regex": query, "$options": "i"}}
                ]
            }
            
            return list(self.stocks_collection.find(search_query).limit(limit))
            
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return []
    
    def get_market_summary(self):
        """Get market summary statistics"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_stocks": {"$sum": 1},
                        "avg_price": {"$avg": "$current_price"},
                        "total_volume": {"$sum": "$volume"},
                        "gainers": {
                            "$sum": {
                                "$cond": [{"$gt": ["$price_change_percent", 0]}, 1, 0]
                            }
                        },
                        "losers": {
                            "$sum": {
                                "$cond": [{"$lt": ["$price_change_percent", 0]}, 1, 0]
                            }
                        }
                    }
                }
            ]
            
            result = list(self.stocks_collection.aggregate(pipeline))
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {}
    
    def get_top_gainers_losers(self, limit=5):
        """Get top gainers and losers"""
        try:
            # Top gainers
            gainers = list(
                self.stocks_collection.find({"price_change_percent": {"$gt": 0}})
                .sort("price_change_percent", -1)
                .limit(limit)
            )
            
            # Top losers
            losers = list(
                self.stocks_collection.find({"price_change_percent": {"$lt": 0}})
                .sort("price_change_percent", 1)
                .limit(limit)
            )
            
            return {"gainers": gainers, "losers": losers}
            
        except Exception as e:
            logger.error(f"Error getting gainers/losers: {e}")
            return {"gainers": [], "losers": []}
    
    def cleanup_old_data(self, days=30):
        """Clean up old price history data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            result = self.price_history_collection.delete_many({
                "date": {"$lt": cutoff_date}
            })
            
            logger.info(f"Cleaned up {result.deleted_count} old price records")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0