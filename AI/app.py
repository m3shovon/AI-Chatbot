from pydantic_ai import Agent 
from pydantic import BaseModel
import yfinance as yf
import asyncio

# for ui
import gradio as gr

class StockMarketData(BaseModel):
    symbol: str
    price: float
    currency: str = "USD"
    message: str

stock_agent = Agent("groq:llama3-70b-8192",
                        result_type=StockMarketData,
                        system_prompt= "Your Helpful Financial Support"
                        
                        )

@stock_agent.tool_plain
def get_stock_price(symbol: str):
    stock = yf.Ticker(symbol)
    # price = stock.history(period="1d")["Close"].values[0]
    price = stock.fast_info.last_price
    return {
        # "symbol": symbol, "price": price, "message": "Here is the stock price for today!"
        "price": round(price, 2),"currency": "USD" , "message": "Here is the stock price for today!"
        }

result = stock_agent.run_sync("what is Apple stock price?")
print(f"Message: {result.data.message}")
print(f"Message: {result.data}")
print(f"Stock Price: {result.data.price:.2f} {result.data.currency}")


# def get_stock_info(query):
#     try:
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         result = loop.run_until_complete(stock_agent.run(query))

#         # result = stock_agent.run_sync(query)
#         response = f"Stock:{result.data.symbol} \n"
#         response = f"Currency:{result.data.currency} \n"
#         response = f"Price:{result.data.price:.2f} \n"
#         response = f"Message:{result.data.message} \n"
#         return response 
#     except Exception as e:
#         return f"Error: {str(e)}"

# demo = gr.Interface(
#     fn=get_stock_info,
#     inputs=gr.Textbox(label="Ask Any Stock info"),
#     outputs=gr.Textbox(label="Stock Info"),
#     # layout=gr.Layout(padding=10),
#     title="Stock Market Data",
#     description="Get the stock market data for any company",
# )    

# if __name__ == '__main__':
#     demo.launch()
