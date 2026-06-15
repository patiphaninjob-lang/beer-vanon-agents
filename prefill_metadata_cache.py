"""
prefill_metadata_cache.py
Prefill metadata (Name, Sector, PE, etc.) for all stocks in US and Thai universes
to avoid slow yfinance Ticker.info calls during the main agent run.
"""

import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf

# US Universe from beer_top100_agent.py
US_UNIVERSE = [
    "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","ORCL","CRM",
    "AMD","ADBE","QCOM","INTC","TXN","AMAT","KLAC","LRCX","MU","MRVL",
    "ADI","NOW","INTU","SNPS","CDNS","CRWD","PANW","FTNT","ZS","IBM",
    "LLY","UNH","JNJ","ABBV","MRK","PFE","BMY","AMGN","GILD","ISRG",
    "SYK","BSX","BDX","DHR","ZTS","ELV","CI","HUM","CVS","HCA",
    "BRK-B","JPM","BAC","WFC","C","GS","MS","AXP","V","MA",
    "BLK","SPGI","MCO","ICE","CME","COF","USB","TFC","PNC","SCHW",
    "HD","MCD","NKE","SBUX","TGT","LOW","DG","BKNG","MAR","HLT",
    "WMT","COST","PG","KO","PEP","PM","MO","CL","MDLZ","GIS",
    "XOM","CVX","COP","SLB","MPC","VLO","OXY","PSX","HAL","BKR",
    "GE","CAT","HON","RTX","LMT","NOC","BA","UPS","DE","UNP",
    "CSX","NSC","ETN","EMR","MMM","ROP",
    "NFLX","TMUS","T","VZ","CMCSA","DIS",
    "LIN","APD","ECL","FCX","NEM","SHW",
    "PLD","AMT","EQIX","CCI","SPG",
    "NEE","SO","DUK","AEP","EXC",
]

# TH Universe from thai_top100_agent.py
TH_UNIVERSE = [
    "AAV.BK", "ADVANC.BK", "AEONTS.BK", "AMATA.BK", "AOT.BK", "AP.BK", "ASW.BK", "AWC.BK", "BAM.BK", "BANPU.BK", 
    "BA.BK", "BBL.BK", "BCH.BK", "BCP.BK", "BCPG.BK", "BDMS.BK", "BEM.BK", "BGRIM.BK", "BH.BK", "BJC.BK", 
    "BLA.BK", "BTG.BK", "BTS.BK", "CBG.BK", "CENTEL.BK", "CHG.BK", "CK.BK", "CKP.BK", "COM7.BK", "CPALL.BK", 
    "CPF.BK", "CPN.BK", "CRC.BK", "DELTA.BK", "DOHOME.BK", "EA.BK", "EGCO.BK", "ERW.BK", "GLOBAL.BK", "GPSC.BK", 
    "GULF.BK", "GUNKUL.BK", "HANA.BK", "HMPRO.BK", "ICHI.BK", "INTUCH.BK", "IRPC.BK", "ITC.BK", "IVL.BK", "JAS.BK", 
    "JMART.BK", "JMT.BK", "KBANK.BK", "KCE.BK", "KKP.BK", "KTB.BK", "KTC.BK", "LANNA.BK", "LH.BK", "MASTER.BK", 
    "MBK.BK", "MC.BK", "MEGA.BK", "MINT.BK", "MTC.BK", "NEX.BK", "OR.BK", "ORI.BK", "OSP.BK", "PLANB.BK", 
    "PRM.BK", "PSH.BK", "PSL.BK", "PTG.BK", "PTT.BK", "PTTEP.BK", "PTTGC.BK", "QH.BK", "RATCH.BK", "SAWAD.BK", 
    "SCB.BK", "SCC.BK", "SCGP.BK", "SINGER.BK", "SIRI.BK", "SISB.BK", "SPALI.BK", "SPRC.BK", "STA.BK", "STEC.BK", 
    "STGT.BK", "TASCO.BK", "TCAP.BK", "THANI.BK", "THG.BK", "TIDLOR.BK", "TIPH.BK", "TISCO.BK", "TKN.BK", "TOP.BK", 
    "TPIPL.BK", "TPIPP.BK", "TRUE.BK", "TTA.BK", "TTB.BK", "TTW.BK", "TU.BK", "TVO.BK", "VGI.BK", "WHA.BK", "WHAUP.BK"
]

def fetch_ticker_metadata(ticker):
    print(f"Fetching {ticker}...")
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        if not info:
            return ticker, None
        
        return ticker, {
            "name": info.get("longName") or info.get("shortName") or ticker,
            "sector": info.get("sector", "N/A"),
            "pe_ratio": info.get("trailingPE"),
            "exchange": info.get("exchange", ""),
            "market_cap": info.get("marketCap", 0)
        }
    except Exception as e:
        print(f"Error {ticker}: {e}")
        return ticker, None

def prefill_cache(tickers, cache_file):
    path = Path(cache_file)
    cache = {}
    if path.exists():
        try:
            cache = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    
    # Only fetch missing ones or refresh if needed
    missing = [t for t in tickers if t not in cache or not cache[t].get("sector") or cache[t].get("sector") == "N/A"]
    print(f"Total: {len(tickers)} | Cached: {len(tickers) - len(missing)} | Missing: {len(missing)}")
    
    if not missing:
        print(f"No missing metadata for {cache_file}")
        return

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_ticker_metadata, missing))
    
    updated = 0
    for ticker, data in results:
        if data:
            # Preserve existing homework if any
            existing = cache.get(ticker, {})
            data["homework_34"] = existing.get("homework_34")
            data["homework_updated"] = existing.get("homework_updated")
            cache[ticker] = data
            updated += 1
    
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {updated} tickers in {cache_file}")

if __name__ == "__main__":
    print("--- US Stocks ---")
    prefill_cache(US_UNIVERSE, "stock_metadata_cache.json")
    
    print("\n--- Thai Stocks ---")
    prefill_cache(TH_UNIVERSE, "thai_metadata_cache.json")
    
    print("\nDone!")
