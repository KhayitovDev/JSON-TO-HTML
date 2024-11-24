from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Any
from fastapi.responses import HTMLResponse

app = FastAPI()

# Define the Pydantic model for the input structure
class Table(BaseModel):
    name: str
    data: List[Any]  # List of data for each table
class NestedDict(BaseModel):
    tables: List[Table]

# Function to recursively flatten complex structures (dict, list, scalar)
def flatten_structure(structure, parent_key='SA'):
    """Recursively flatten a nested structure (dict, list, or scalar)."""
    flattened = {}

    if isinstance(structure, dict):  # If it's a dictionary, iterate through key-value pairs
        for key, value in structure.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            flattened.update(flatten_structure(value, new_key))  # Recursively process nested structures

    elif isinstance(structure, list):  # If it's a list, process each item
        for idx, item in enumerate(structure):
            new_key = f"{parent_key}[{idx}]"
            flattened.update(flatten_structure(item, new_key))  # Recursively process each list item

    else:  # If it's a scalar value (string, integer, etc.), just return the value
        flattened[parent_key] = structure

    return flattened

@app.post("/convert_to_html", response_class=HTMLResponse)
async def convert_to_html(request: NestedDict):
    html = """
    <html>
      <head>
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background-color: #f4f4f9;
          }
          h2 {
            color: #333;
            font-size: 1.8em;
            margin-top: 40px;
            margin-bottom: 10px;
          }
          table {
            width: 80%;
            margin-bottom: 30px;
            border-collapse: collapse;
            background-color: #fff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
          }
          th, td {
            padding: 10px 15px;
            text-align: left;
            border: 1px solid #ddd;
          }
          th {
            background-color: #007bff;
            color: white;
          }
          tr:nth-child(even) {
            background-color: #f2f2f2;
          }
          tr:hover {
            background-color: #ddd;
          }
          td {
            color: #333;
          }
        </style>
      </head>
      <body>
    """
    
    # Loop through each table in the JSON
    for table in request.tables:
        html += f"<h2>{table.name}</h2>"  # Add table name as a header
        
        data = table.data
        if not data:
            html += "<p>No data provided for this table.</p>"
            continue
        
        # Flatten the data
        flattened_data = []
        all_keys = set()  # To keep track of all possible keys for table headers
        
        for entry in data:
            flattened_row = flatten_structure(entry)  # Flatten each row
            flattened_data.append(flattened_row)
            all_keys.update(flattened_row.keys())  # Add all keys to the header set
        
        # Generate table header
        html += "<table>"
        html += "<thead><tr>"
        for key in all_keys:
            html += f"<th>{key}</th>"
        html += "</tr></thead>"

        # Generate table rows
        html += "<tbody>"
        for flattened_row in flattened_data:
            html += "<tr>"
            for key in all_keys:
                html += f"<td>{flattened_row.get(key, '')}</td>"  # Empty if key is not in the row
            html += "</tr>"
        html += "</tbody>"

        html += "</table>"
    
    html += """
      </body>
    </html>
    """
    return html
