from sqlalchemy import create_engine, MetaData, Table, select

# Database connection
DATABASE_URL = "postgresql+psycopg2://postgres:cimxDZDVXtvFhBMSyFVxtzLDNVWyFrTK@monorail.proxy.rlwy.net:57837/railway"  
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)
products = metadata.tables['productDetails']

def search_products(query):
    """
    Search for products in the database based on the user's query.
    """
    with engine.connect() as connection:
        stmt = select([products]).where(products.c.name.like(f'%{query}%'))
        results = connection.execute(stmt).fetchall()
        return results

def chatbot_response(user_input):
    """
    Generate a response based on the user's input.
    """
    if "product" in user_input.lower():
        product_name = user_input.lower().replace("product", "").strip()
        results = search_products(product_name)
        if results:
            response = "Here are the products I found:\n"
            for product in results:
                response += f"{product.name} - ${product.price}\n"
        else:
            response = "Sorry, I couldn't find any products matching your query."
    else:
        response = "I can help you find products. Please ask about a specific product."
    return response

def run_chatbot():
    """
    Run the chatbot in a loop for user interaction.
    """
    print("Welcome to the E-commerce Chatbot! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye! Have a great day!")
            break
        response = chatbot_response(user_input)
        print(f"Chatbot: {response}")

# Run the chatbot
if __name__ == "__main__":
    run_chatbot()