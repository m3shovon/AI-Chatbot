from sqlalchemy import create_engine, MetaData, Table, select, text, func
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Pydantic Models
class Product(BaseModel):
    id: int
    title: str  
    Short_description: Optional[str] 
    product_discount_price: float  
    max_price: float  
    quantity: int
    product_code: Optional[str]  
    created_at: datetime = Field(default_factory=datetime.now)

class ChatResponse(BaseModel):
    message: str
    products: Optional[List[Product]] = None

class AIAgent:
    def __init__(self):
        # Database connection
        self.DATABASE_URL = "postgresql://postgres.mlmuzrxjryqzxukuqtsz:g91IneqRjVCtrNuW@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
        self.engine = create_engine(self.DATABASE_URL)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.products_table = self.metadata.tables['product_productdetails']

        # Initialize OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def search_products(self, query: str) -> List[Product]:
        """Search for products in the database with advanced query handling"""
        with self.engine.connect() as connection:
            try:
                # debug info
                print(f"Searching for: {query}")
                
                # search case-insensitive and exact for product codes
                stmt = select(self.products_table).where(
                    (func.lower(self.products_table.c.product_code) == func.lower(query)) |
                    (func.lower(self.products_table.c.product_code).like(f'%{query.lower()}%')) |
                    (func.lower(self.products_table.c.title).like(f'%{query.lower()}%')) |
                    (func.lower(self.products_table.c.Short_description).like(f'%{query.lower()}%'))
                )
                
                # Execute query and fetch results
                results = connection.execute(stmt).fetchall()
                
                # Print debug information
                print(f"Found {len(results)} results")
                if len(results) == 0:
                    check_stmt = select(self.products_table.c.product_code).limit(5)
                    sample_codes = connection.execute(check_stmt).fetchall()
                    print("Sample product codes in database:", [code[0] for code in sample_codes])
                
                return [Product(
                    id=row.id,
                    title=row.title,
                    Short_description=row.Short_description,
                    product_discount_price=float(row.product_discount_price),
                    max_price=float(row.max_price),
                    quantity=row.quantity,
                    product_code=row.product_code,
                    created_at=datetime.now()
                ) for row in results]
                
            except Exception as e:
                print(f"Database search error: {str(e)}")
                return []

    def get_product_count(self, product_code: str) -> int:
        """Get the quantity of a specific product"""
        with self.engine.connect() as connection:
            stmt = select(self.products_table.c.quantity).where(
                self.products_table.c.product_code.ilike(f'%{product_code}%')
            )
            result = connection.execute(stmt).first()
            return result.quantity if result else 0

    async def get_ai_response(self, user_input: str) -> ChatResponse:
        """Generate AI response using OpenAI"""
        system_prompt = """
        You are an intelligent e-commerce assistant. You help users with:
        1. Finding product information
        2. Checking product quantities
        3. Answering questions about product availability
        4. Providing product recommendations
        
        When users ask about quantities or availability, provide specific numbers.
        Be concise but friendly in your responses.
        If a product is not found, suggest checking the product code format.
        """

        # Clean the input query
        query = user_input.strip().upper() if "find" in user_input.lower() else user_input
        products = self.search_products(query)
        
        if "find" in user_input.lower() and not products:
            return ChatResponse(
                message=f"I couldn't find any products with the code '{query}'. Please verify the product code and try again. "
                       f"Make sure the code format is correct (e.g., TEST0200121).",
                products=None
            )

        # Handle quantity-specific queries
        if "how many" in user_input.lower() or "quantity" in user_input.lower():
            product_counts = []
            for product in products:
                product_counts.append(f"{product.title} (Code: {product.product_code}): {product.quantity} units")
            
            product_context = "\n".join(product_counts) if product_counts else "No matching products found."
        else:
            product_context = "\n".join([
                f"- {p.title} (Code: {p.product_code}): ${p.max_price} - ${p.product_discount_price} - {p.Short_description} (Quantity: {p.quantity})" 
                for p in products
            ]) if products else "No specific products found."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User Query: {user_input}\nAvailable Products Info: {product_context}"}
                ]
            )
            
            ai_message = response.choices[0].message.content

            return ChatResponse(
                message=ai_message,
                products=products if products else None
            )
        except Exception as e:
            # Fallback response if OpenAI fails
            if products:
                return ChatResponse(
                    message=f"Here's what I found:\n{product_context}",
                    products=products
                )
            return ChatResponse(
                message="I apologize, but I couldn't find any products matching your query.",
                products=None
            )

def run_chatbot():
    """Run the chatbot in an interactive loop"""
    import asyncio
    
    agent = AIAgent()
    print("Welcome to the AI E-commerce Assistant! Type 'exit' to quit.")
    
    async def chat_loop():
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Assistant: Goodbye! Have a great day!")
                break
                
            response = await agent.get_ai_response(user_input)
            print(f"\nAssistant: {response.message}")
            
            if response.products:
                print("\nFound Products:")
                for product in response.products:
                    print(f"- {product.title} (Code: {product.product_code}): ${product.product_discount_price}: ${product.max_price}")
            print()

    asyncio.run(chat_loop())

if __name__ == "__main__":
    run_chatbot()