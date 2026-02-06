from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import time 
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Update CORS to allow ngrok
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://fin-board-silk-sigma.vercel.app",
            "https://faucal-margaret-lowerable.ngrok-free.dev/api/stocks",
            "https://*.ngrok-free.app",  # New ngrok domain
            "https://*.ngrok.io",         # Old ngrok domain
            "http://localhost:3000",
            "http://localhost:5173"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type","ngrok-skip-browser-warning"],
        "expose_headers": ["*"],
        "supports_credentials": False
    }
})


# Cache configuration - Increase to 3 minutes
CACHE = {
    "data": None,
    "last_updated": None, 
    "cache_duration": timedelta(minutes=30)
}

PORTFOLIO_STOCKS = {
    "Financial Sector": {
        "HDFCBANK.NS": "HDFC Bank",
        "BAJFINANCE.NS": "Bajaj Finance",
        "ICICIBANK.NS": "ICICI Bank",
        "BAJAJHFL.NS": "Bajaj Housing",
        "SAVAFINANCIAL.BO": "Savani Financials",
        "SBILIFE.NS": "SBI Life",
    },
    "Tech Sector": {
        "AFFLE.NS": "Affle India",
        "LTIM.NS": "LTI Mindtree",
        "KPITTECH.NS": "KPIT Tech",
        "TATATECH.NS": "Tata Tech",
        "BLSE.NS": "BLS E-Services",
        "TANLA.NS": "Tanla Platforms",
        "INFY.NS": "Infosys",
        "HAPPSTMNDS.NS": "Happiest Minds",
    },
    "Consumer Sector": {
        "DMART.NS": "DMart",
        "TATACONSUM.NS": "Tata Consumer",
        "PIDILITIND.NS": "Pidilite",
    },
    "Power Sector": {
        "TATAPOWER.NS": "Tata Power",
        "KPIGREEN.NS": "KPI Green",
        "SUZLON.NS": "Suzlon",
        "GENSOL.NS": "Gensol",
    },
    "Pipe Sector": {
        "HARIOMPIPE.NS": "Hariom Pipes",
        "ASTRAL.NS": "Astral",
        "POLYCAB.NS": "Polycab",
    },
    "Others": {
        "CLEAN.NS": "Clean Science",
        "DEEPAKNTR.NS": "Deepak Nitrite",
        "FINEORG.NS": "Fine Organic",
        "GRAVITA.NS": "Gravita",
        "EASEMYTRIP.NS": "Easemytrip",
    }
}

def get_stock_details():
    """Fetch detailed stock information for all portfolio stocks"""

    # Check if cache is valid or not
    if CACHE["data"] and CACHE["last_updated"]:
        time_since_update = datetime.now() - CACHE["last_updated"]
        if time_since_update < CACHE["cache_duration"]:
            print(f"Returning cached data (age: {time_since_update.total_seconds():.0f}s)")
            return CACHE["data"]
    
    print("Cache expired or empty. Fetching fresh data...")
    results = []
    
    # Storing symbol sector and company name
    symbol_mapping = {}
    all_symbols = []

    for sector, stocks in PORTFOLIO_STOCKS.items():
        for symbol, company_name in stocks.items():
            symbol_mapping[symbol] = {
                "sector": sector,
                "company_name": company_name
            }
            all_symbols.append(symbol)



    # Process each stock in the batch
    for symbol in all_symbols:
            try:
                ticker = yf.Ticker(symbol)
                
                # Get basic info first
                info = ticker.info
                
                # Get current market price
                hist = ticker.history(period="1d")
                cmp = round(hist['Close'].iloc[-1], 2) if not hist.empty else info.get('currentPrice')
                
                # Financial metrics
                market_cap = info.get('marketCap')
                pe_ratio = round(info.get('trailingPE'), 2) if info.get('trailingPE') else None
                revenue_ttm = info.get('totalRevenue')
                ebitda_ttm = info.get('ebitda')
                pat = info.get('netIncomeToCommon')
                
                # Calculate percentages
                ebitda_pct = round((ebitda_ttm / revenue_ttm * 100), 2) if ebitda_ttm and revenue_ttm else None
                pat_pct = round((pat / revenue_ttm * 100), 2) if pat and revenue_ttm else None
                
                # Add delay before cashflow request (expensive operation)
                time.sleep(random.uniform(0.5, 1.0))
                
                # Cash flow data
                cfo_march_24 = None
                cfo_5_years = None
                free_cash_flow_5_years = None
                
                try:
                    cashflow = ticker.cashflow
                    if not cashflow.empty:
                        if 'Operating Cash Flow' in cashflow.index:
                            cfo_data = cashflow.loc['Operating Cash Flow']
                            if len(cfo_data) > 0:
                                cfo_march_24 = int(cfo_data.iloc[0])
                            if len(cfo_data) >= 5:
                                cfo_5_years = int(cfo_data.iloc[:5].sum())
                        
                        if 'Free Cash Flow' in cashflow.index:
                            fcf_data = cashflow.loc['Free Cash Flow']
                            if len(fcf_data) >= 5:
                                free_cash_flow_5_years = int(fcf_data.iloc[:5].sum())
                except Exception as cf_error:
                    print(f"  Warning: Could not fetch cashflow for {symbol}: {str(cf_error)}")
                
                # Balance sheet data
                debt_to_equity = info.get('debtToEquity')
                book_value = round(info.get('bookValue'), 2) if info.get('bookValue') else None
                
                # Ratios
                price_to_sales = round(info.get('priceToSalesTrailing12Months'), 2) if info.get('priceToSalesTrailing12Months') else None
                cfo_to_ebitda = round((cfo_march_24 / ebitda_ttm), 2) if cfo_march_24 and ebitda_ttm else None
                cfo_to_pat = round((cfo_march_24 / pat), 2) if cfo_march_24 and pat else None
                price_to_book = round(info.get('priceToBook'), 2) if info.get('priceToBook') else None
                
                stock_data = {
                    "sector": symbol_mapping[symbol]["sector"],
                    "symbol": symbol,
                    "company_name": symbol_mapping[symbol]["company_name"],
                    "cmp": cmp,
                    "market_cap": market_cap,
                    "pe_ratio": pe_ratio,
                    "latest_earnings": pat,
                    "revenue_ttm": revenue_ttm,
                    "ebitda_ttm": ebitda_ttm,
                    "ebitda_percentage": ebitda_pct,
                    "pat": pat,
                    "pat_percentage": pat_pct,
                    "cfo_march_24": cfo_march_24,
                    "cfo_5_years": cfo_5_years,
                    "free_cash_flow_5_years": free_cash_flow_5_years,
                    "debt_to_equity": debt_to_equity,
                    "book_value": book_value,
                    "price_to_sales": price_to_sales,
                    "cfo_to_ebitda": cfo_to_ebitda,
                    "cfo_to_pat": cfo_to_pat,
                    "price_to_book": price_to_book
                }
                
                results.append(stock_data)
                print(f"  ✓ {symbol}")
                
            except Exception as e:
                error_msg = str(e)
                print(f"  ✗ {symbol}: {error_msg}")
                
                # If we hit rate limit, wait longer
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    print("  ⚠️  Rate limit detected! Waiting 10 seconds...")
                    time.sleep(10)
                
                results.append({
                    "sector": symbol_mapping[symbol]["sector"],
                    "symbol": symbol,
                    "company_name": symbol_mapping[symbol]["company_name"],
                    "error": error_msg
                })
    
    # Update the cache
    CACHE["data"] = results
    CACHE["last_updated"] = datetime.now()
    
    print(f"✓ Successfully fetched {len(results)} stocks. Cache updated.")
    return results

def get_current_market_price():
    """Fetch detailed stock information for all portfolio stocks"""
    results = []
    
    # Storing symbol sector and company name
    symbol_mapping = {}
    all_symbols = []

    for sector, stocks in PORTFOLIO_STOCKS.items():
        for symbol, company_name in stocks.items():
            symbol_mapping[symbol] = {
                "sector": sector,
                "company_name": company_name
            }
            all_symbols.append(symbol)

    # Process each stock in the batch
    for symbol in all_symbols:
            try:
                ticker = yf.Ticker(symbol)
                
                # Get basic info first
                info = ticker.info
                
                # Get current market price
                hist = ticker.history(period="1d")
                cmp = round(hist['Close'].iloc[-1], 2) if not hist.empty else info.get('currentPrice')
                
                stock_data = {
                    "cmp": cmp,
                }
                results.append(stock_data)
                print(f"  ✓ {symbol}")
                
            except Exception as e:
                error_msg = str(e)
                print(f"  ✗ {symbol}: {error_msg}")
                
                # If we hit rate limit, wait longer
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    print("  ⚠️  Rate limit detected! Waiting 10 seconds...")
                    time.sleep(10)
                
                results.append({
                    "sector": symbol_mapping[symbol]["sector"],
                    "symbol": symbol,
                    "company_name": symbol_mapping[symbol]["company_name"],
                    "error": error_msg
                })
    
    return results


@app.route('/api/stocks', methods=['GET'])
def get_all_stocks():
    """API endpoint to get all portfolio stocks data"""
    try:
        stocks_data = get_stock_details()
        return jsonify({
            "success": True,
            "total_stocks": len(stocks_data),
            "cached": CACHE["last_updated"] is not None,
            "cache_expires_in": int((CACHE["cache_duration"] - (datetime.now() - CACHE["last_updated"])).total_seconds()) if CACHE["last_updated"] else None,
            "last_updated": CACHE["last_updated"].isoformat() if CACHE["last_updated"] else None,
            "data": stocks_data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/prices', methods=['GET'])
def get_live_prices():
    """API endpoint to get all portfolio stocks data"""
    try:
        stocks_cmp = get_current_market_price()
        return jsonify({
            "success": True,
            "total_stocks": len(stocks_cmp),
            "data": stocks_cmp
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    cache_age = None
    if CACHE["last_updated"]:
        cache_age = int((datetime.now() - CACHE["last_updated"]).total_seconds())
    
    return jsonify({
        "status": "healthy",
        "message": "Finance API is running",
        "cache_status": {
            "is_cached": CACHE["data"] is not None,
            "last_updated": CACHE["last_updated"].isoformat() if CACHE["last_updated"] else None,
            "cache_age_seconds": cache_age,
            "cache_duration_seconds": int(CACHE["cache_duration"].total_seconds())
        }
    })


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)