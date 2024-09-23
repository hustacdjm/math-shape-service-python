# In-memory database (for demonstration purposes)
items = [
    {"id":1, "title":"Book 1", "author":"Author 1"},
    {"id":2, "title":"Book 2", "author":"Author 2"},
    {"id":3, "title":"Book 3", "author":"Author 3"}
]

def get_items():
    return {'items': items}

def get_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item is not None:
        return item
    return {'error': 'Item not found'}


