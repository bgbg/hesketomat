import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import faiss
import numpy as np
import sqlite3
from typing import List


class VectorStore:
    def __init__(
        self, dim: int, index_path: str = "vectors.index", db_path: str = "metadata.db"
    ):
        self.dim = dim
        self.index_path = index_path
        self.db_path = db_path

        # Initialize or load Faiss index
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        else:
            self.index = faiss.IndexFlatL2(dim)

        # Initialize SQLite for metadata
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                description TEXT
            )
        """
        )
        self.conn.commit()

    def add_item(self, description: str, embedding: List[float]) -> None:
        """Add an item with its embedding."""
        vector = np.array([embedding], dtype=np.float32)
        self.index.add(vector)

        # Store metadata
        self.conn.execute("INSERT INTO items (description) VALUES (?)", (description,))
        self.conn.commit()

        # Save index to disk
        faiss.write_index(self.index, self.index_path)

    def search_similar(
        self, query_embedding: List[float], limit: int = 3
    ) -> List[tuple]:
        """Find most similar items."""
        query = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query, limit)

        # Get metadata for results
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            description = self.conn.execute(
                "SELECT description FROM items WHERE id = ?",
                (int(idx) + 1,),  # SQLite rowid starts at 1
            ).fetchone()[0]
            similarity = 1 / (1 + dist)  # Convert L2 distance to similarity score
            results.append((description, similarity))
        return results


def main():
    # Initialize store with 3D vectors
    store = VectorStore(dim=3)

    # Sample data
    items = [
        ("red apple", [1.0, 0.2, 0.1]),
        ("green apple", [0.9, 0.3, 0.1]),
        ("banana", [0.1, 0.8, 0.9]),
        ("orange", [0.4, 0.7, 0.6]),
    ]

    # Add items
    for desc, emb in items:
        store.add_item(desc, emb)

    # Search example
    query = [1.0, 0.2, 0.1]  # Similar to "red apple"
    results = store.search_similar(query)

    print("Search results (item, similarity score):")
    for item, similarity in results:
        print(f"{item}: {similarity:.3f}")


if __name__ == "__main__":
    main()
