import sqlite3
import json
from typing import List, Any, Dict
import numpy as np
from datetime import datetime
from objects.node import NODE_PROPERTIES
import os

class NodeStorage:
    def __init__(self, raw_data_dir: str, db_path: str):
        self.raw_data_dir = raw_data_dir
        os.makedirs(raw_data_dir, exist_ok=True)
        self.db_manager = SQLiteManager(db_path)

    def save_node(self, node_data: Dict[str, Any]) -> str:
        # Generate a unique ID for the node
        node_id = self._generate_unique_id()
        
        # Save raw data to file
        file_path = os.path.join(self.raw_data_dir, f"{node_id}.json")
        with open(file_path, 'w') as f:
            json.dump(node_data, f)
        
        # Insert into SQLite database
        db_data = self._prepare_db_data(node_data)
        db_data['id'] = node_id
        self.db_manager.insert_node(db_data)
        
        return node_id

    def get_node(self, node_id: str) -> Dict[str, Any]:
        # Retrieve raw data from file
        file_path = os.path.join(self.raw_data_dir, f"{node_id}.json")
        with open(file_path, 'r') as f:
            node_data = json.load(f)
        
        # Retrieve additional data from SQLite if needed
        db_data = self.db_manager.get_node(node_id)
        if db_data:
            node_data.update(db_data)
        
        return node_data

    def update_node(self, node_id: str, update_data: Dict[str, Any]):
        # Update raw data file
        file_path = os.path.join(self.raw_data_dir, f"{node_id}.json")
        with open(file_path, 'r') as f:
            node_data = json.load(f)
        node_data.update(update_data)
        with open(file_path, 'w') as f:
            json.dump(node_data, f)
        
        # Update SQLite database
        db_data = self._prepare_db_data(update_data)
        self.db_manager.update_node(node_id, db_data)

    def delete_node(self, node_id: str):
        # Delete raw data file
        file_path = os.path.join(self.raw_data_dir, f"{node_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from SQLite database
        self.db_manager.delete_node(node_id)

    def vector_search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        # Perform vector search using SQLite database
        results = self.db_manager.vector_search(query_vector, top_k)
        
        # Retrieve full node data for each result
        return [self.get_node(result['id']) for result in results]

    def _generate_unique_id(self) -> str:
        # Implement a method to generate a unique ID (e.g., UUID)
        import uuid
        return str(uuid.uuid4())

    def _prepare_db_data(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        # Prepare a subset of node_data for database storage
        db_fields = [prop.name for prop in NODE_PROPERTIES]
        return {k: v for k, v in node_data.items() if k in db_fields}

class SQLiteManager:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Dynamically create table based on NodeProperty instances
        columns = []
        for prop in NODE_PROPERTIES:
            col_type = self._get_sqlite_type(prop.datatype)
            nullable = "NOT NULL" if prop.mode == "REQUIRED" else ""
            columns.append(f"{prop.name} {col_type} {nullable}")
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {', '.join(columns)}
        )
        """
        self.cursor.execute(create_table_sql)
        self.conn.commit()

    def _get_sqlite_type(self, datatype: str) -> str:
        type_mapping = {
            "str": "TEXT",
            "List[str]": "TEXT",
            "datetime": "TIMESTAMP",
            "List[float]": "BLOB"
        }
        return type_mapping.get(datatype, "TEXT")

    def insert_node(self, node_data: Dict[str, Any]):
        columns = []
        placeholders = []
        values = []
        for prop in NodeProperty.get_instances():
            if prop.name in node_data:
                columns.append(prop.name)
                placeholders.append('?')
                value = node_data[prop.name]
                if prop.datatype == "List[str]":
                    value = json.dumps(value)
                elif prop.datatype == "List[float]":
                    value = np.array(value, dtype=np.float32).tobytes()
                elif prop.datatype == "datetime":
                    value = value.isoformat()
                values.append(value)

        insert_sql = f"INSERT INTO nodes ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        self.cursor.execute(insert_sql, values)
        self.conn.commit()
        return self.cursor.lastrowid

    def get_node(self, node_id: int) -> Dict[str, Any]:
        self.cursor.execute("SELECT * FROM nodes WHERE id = ?", (node_id,))
        row = self.cursor.fetchone()
        if row:
            column_names = [description[0] for description in self.cursor.description]
            node_data = dict(zip(column_names, row))
            for prop in NodeProperty.get_instances():
                if prop.datatype == "List[str]":
                    node_data[prop.name] = json.loads(node_data[prop.name]) if node_data[prop.name] else []
                elif prop.datatype == "List[float]":
                    node_data[prop.name] = np.frombuffer(node_data[prop.name], dtype=np.float32).tolist() if node_data[prop.name] else []
                elif prop.datatype == "datetime":
                    node_data[prop.name] = datetime.fromisoformat(node_data[prop.name]) if node_data[prop.name] else None
            return node_data
        return None

    def update_node(self, node_id: int, update_data: Dict[str, Any]):
        set_clauses = []
        values = []
        for prop in NodeProperty.get_instances():
            if prop.name in update_data:
                set_clauses.append(f"{prop.name} = ?")
                value = update_data[prop.name]
                if prop.datatype == "List[str]":
                    value = json.dumps(value)
                elif prop.datatype == "List[float]":
                    value = np.array(value, dtype=np.float32).tobytes()
                elif prop.datatype == "datetime":
                    value = value.isoformat()
                values.append(value)
        
        update_sql = f"UPDATE nodes SET {', '.join(set_clauses)} WHERE id = ?"
        values.append(node_id)
        self.cursor.execute(update_sql, values)
        self.conn.commit()

    def delete_node(self, node_id: int):
        self.cursor.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
        self.conn.commit()

    def vector_search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        query_vector = np.array(query_vector, dtype=np.float32)
        self.cursor.execute("SELECT id, embedding FROM nodes")
        results = []
        for row in self.cursor.fetchall():
            id, embedding_bytes = row
            if embedding_bytes:
                embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                similarity = 1 - np.linalg.norm(query_vector - embedding)
                results.append((id, similarity))
        
        results.sort(key=lambda x: x[1], reverse=True)
        top_results = results[:top_k]
        
        return [self.get_node(id) for id, _ in top_results]

    def close(self):
        self.conn.close()

# Example usage
if __name__ == "__main__":
    db_manager = SQLiteManager('nodes.db')
    
    # Example node data
    node_data = {
        "label": "Personal Note",
        "author": ["John Doe"],
        "creation_date": datetime.now(),
        "modification_date": datetime.now(),
        "filetype": "text",
        "location": "Local Files",
        "path": "/path/to/file",
        "research_question": "How does X affect Y?",
        "main_argument": "X has a significant impact on Y",
        "summary": "This note explores the relationship between X and Y...",
        "tags": ["tag1", "tag2"],
        "themes": ["theme1", "theme2"],
        "keywords": ["keyword1", "keyword2"],
        "quotes": ["quote1", "quote2"],
        "entities_persons": ["Person A", "Person B"],
        "entities_places": ["Place A", "Place B"],
        "entities_organizations": ["Org A", "Org B"],
        "entities_references": ["Ref 1", "Ref 2"],
        "embedding": [0.1, 0.2, 0.3, 0.4]
    }

    # Insert a node
    node_id = db_manager.insert_node(node_data)
    print(f"Inserted node with ID: {node_id}")

    # Retrieve the node
    retrieved_node = db_manager.get_node(node_id)
    print(f"Retrieved node: {retrieved_node}")

    # Update the node
    db_manager.update_node(node_id, {"summary": "Updated summary..."})

    # Perform a vector search
    search_results = db_manager.vector_search([0.1, 0.2, 0.3, 0.4])
    print(f"Search results: {search_results}")

    # Delete the node
    db_manager.delete_node(node_id)

    db_manager.close()