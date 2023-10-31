from fastapi import FastAPI
from routers.wellknown import wellknown
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()
app.include_router(wellknown)
app.add_middleware(CORSMiddleware, allow_origins=["https://www.bing.com", "https://localhost", "http://localhost"])

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}

@app.post("/todos/<string:username>")
async def add_todo(username):
    request = await app.middleware.request.get_json(force=True)
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(request["todo"])
    return app.middleware.Response(response='OK', status=200)

@app.get("/todos/<string:username>")
async def get_todos(username):
    return app.middleware.Response(response=json.dumps(_TODOS.get(username, [])), status=200)

@app.delete("/todos/<string:username>")
async def delete_todo(username):
    request = await app.middleware.request.get_json(force=True)
    todo_idx = request["todo_idx"]
    # fail silently, it's a simple plugin
    if 0 <= todo_idx < len(_TODOS[username]):
        _TODOS[username].pop(todo_idx)
    return app.middleware.Response(response='OK', status=200)


with open("./data/products.json", "r") as f:
    products = json.load(f)


@app.get("/products", summary="Get a list of products", operation_id="getProducts")
async def get_products(query: str = None):
    """
    Returns a list of products, optionally filtered by providing a query parameter.
    """
    if query:
        keywords = query.lower().split()
        return [
            product
            for product in products
            if all(keyword in str(product.values()).lower() for keyword in keywords)
        ]
    return products
