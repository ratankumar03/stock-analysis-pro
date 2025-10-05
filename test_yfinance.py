# test_yfinance.py
# Run this in your Django project directory: python test_yfinance.py

import yfinance as yf
import pandas as pd

def test_yfinance():
    print("Testing yfinance library...")
    
    try:
        # Test with MSFT
        print("\n1. Testing MSFT...")
        stock = yf.Ticker("MSFT")
        
        # Get basic info
        info = stock.info
        print(f"Company Name: {info.get('longName', 'Not found')}")
        print(f"Current Price: ${info.get('regularMarketPrice', 'Not found')}")
        
        # Get historical data
        hist = stock.history(period="5d")
        print(f"Historical data shape: {hist.shape}")
        print(f"Latest close price: ${hist['Close'].iloc[-1]:.2f}")
        
        if hist.empty:
            print("ERROR: Historical data is empty!")
            return False
        
        print("✓ MSFT data fetched successfully")
        
        # Test with another stock
        print("\n2. Testing AAPL...")
        aapl = yf.Ticker("AAPL")
        aapl_hist = aapl.history(period="5d")
        
        if not aapl_hist.empty:
            print(f"✓ AAPL latest close: ${aapl_hist['Close'].iloc[-1]:.2f}")
        else:
            print("ERROR: AAPL data is empty!")
            
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_yfinance()
    if success:
        print("\n✓ yfinance is working correctly!")
    else:
        print("\n✗ yfinance has issues. Check your internet connection and try installing/updating yfinance:")
        print("pip install --upgrade yfinance")