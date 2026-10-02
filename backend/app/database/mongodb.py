import json
import os
import time
from typing import Dict, Any, List, Optional
from backend.app.config import settings, logger

class MongoDBClient:
    """
    Production-grade MongoDB client using PyMongo with fallback local JSON persistence.
    Manages 5 core collections:
    1. users
    2. schemes
    3. conversation_memory
    4. feedback
    5. uploaded_pdfs
    """
    COLLECTIONS = ["users", "schemes", "conversation_memory", "feedback", "uploaded_pdfs"]

    def __init__(self):
        self.db_name = settings.MONGODB_DB_NAME
        self.connected = False
        self.db = None
        self.mongo_client = None
        
        # Local JSON fallback store
        self.fallback_dir = "backend/data"
        os.makedirs(self.fallback_dir, exist_ok=True)
        self.local_store: Dict[str, List[Dict[str, Any]]] = {c: [] for c in self.COLLECTIONS}

        self._init_connection()
        self._load_seed_data()

    def _init_connection(self):
        try:
            import pymongo
            # Short timeout to quickly fall back if MongoDB isn't running locally
            self.mongo_client = pymongo.MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=1500)
            self.mongo_client.admin.command('ping')
            self.db = self.mongo_client[self.db_name]
            self.connected = True
            logger.info(f"Successfully connected to MongoDB server at {settings.MONGODB_URI} (DB: {self.db_name})")
        except Exception as e:
            self.connected = False
            logger.warning(f"MongoDB connection unestablished: {e}. Utilizing persistent JSON fallback mode.")
            self._load_local_store()

    def _load_local_store(self):
        for col in self.COLLECTIONS:
            file_path = os.path.join(self.fallback_dir, f"db_{col}.json")
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.local_store[col] = json.load(f)
                except Exception as e:
                    logger.error(f"Error reading local store for {col}: {e}")

    def _sync_local_store(self, collection_name: str):
        if collection_name in self.COLLECTIONS:
            file_path = os.path.join(self.fallback_dir, f"db_{collection_name}.json")
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.local_store[collection_name], f, indent=2)
            except Exception as e:
                logger.error(f"Error syncing local store for {collection_name}: {e}")

    def _load_seed_data(self):
        # Load sample schemes if schemes collection is empty
        schemes = self.find_all("schemes")
        if not schemes and os.path.exists(settings.SAMPLE_SCHEMES_PATH):
            try:
                with open(settings.SAMPLE_SCHEMES_PATH, "r", encoding="utf-8") as f:
                    seed_schemes = json.load(f)
                for scheme in seed_schemes:
                    self.insert_one("schemes", scheme)
                logger.info(f"Seeded {len(seed_schemes)} initial government schemes into database.")
            except Exception as e:
                logger.error(f"Failed to seed initial schemes: {e}")

    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
        doc = dict(document)
        if "_id" not in doc:
            doc["_id"] = f"{collection_name}_{time.time_ns()}"
        doc["created_at"] = time.time()

        if self.connected and self.db is not None:
            try:
                self.db[collection_name].insert_one(doc)
                return doc
            except Exception as e:
                logger.error(f"MongoDB insert error in '{collection_name}': {e}. Writing to fallback.")

        if collection_name not in self.local_store:
            self.local_store[collection_name] = []
        self.local_store[collection_name].append(doc)
        self._sync_local_store(collection_name)
        return doc

    def find_all(self, collection_name: str) -> List[Dict[str, Any]]:
        if self.connected and self.db is not None:
            try:
                docs = list(self.db[collection_name].find({}))
                for d in docs:
                    if isinstance(d.get("_id"), str):
                        pass
                    else:
                        d["_id"] = str(d["_id"])
                return docs
            except Exception as e:
                logger.error(f"MongoDB find_all error in '{collection_name}': {e}. Using fallback.")

        return self.local_store.get(collection_name, [])

    def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self.connected and self.db is not None:
            try:
                doc = self.db[collection_name].find_one(query)
                if doc and not isinstance(doc.get("_id"), str):
                    doc["_id"] = str(doc["_id"])
                return doc
            except Exception as e:
                logger.error(f"MongoDB find_one error in '{collection_name}': {e}. Using fallback.")

        docs = self.local_store.get(collection_name, [])
        for doc in docs:
            match = all(doc.get(k) == v for k, v in query.items())
            if match:
                return doc
        return None

    def update_one(self, collection_name: str, query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        if self.connected and self.db is not None:
            try:
                res = self.db[collection_name].update_one(query, {"$set": update_data})
                return res.modified_count > 0 or res.matched_count > 0
            except Exception as e:
                logger.error(f"MongoDB update_one error in '{collection_name}': {e}. Using fallback.")

        docs = self.local_store.get(collection_name, [])
        for doc in docs:
            if all(doc.get(k) == v for k, v in query.items()):
                doc.update(update_data)
                self._sync_local_store(collection_name)
                return True
        return False

    def delete_one(self, collection_name: str, query: Dict[str, Any]) -> bool:
        if self.connected and self.db is not None:
            try:
                res = self.db[collection_name].delete_one(query)
                return res.deleted_count > 0
            except Exception as e:
                logger.error(f"MongoDB delete_one error in '{collection_name}': {e}. Using fallback.")

        docs = self.local_store.get(collection_name, [])
        initial_count = len(docs)
        self.local_store[collection_name] = [d for d in docs if not all(d.get(k) == v for k, v in query.items())]
        deleted = len(self.local_store[collection_name]) < initial_count
        if deleted:
            self._sync_local_store(collection_name)
        return deleted

db = MongoDBClient()
