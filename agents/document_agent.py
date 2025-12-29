"""
Document agent for RAG-based search over policy documents.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class DocumentAgent:
    """Agent for searching policy documents using RAG."""

    def __init__(
        self,
        docs_dir: str = "./data/documents",
        vectors_dir: str = "./data/vectors"
    ):
        self.docs_dir = Path(docs_dir)
        self.vectors_dir = Path(vectors_dir)
        self.collection = None

        if CHROMADB_AVAILABLE:
            self._init_chromadb()

    def _init_chromadb(self):
        """Initialize ChromaDB with sentence transformers."""
        try:
            self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self.client = chromadb.PersistentClient(path=str(self.vectors_dir))
            self.collection = self.client.get_or_create_collection(
                name="policy_documents",
                embedding_function=self.ef
            )
        except Exception as e:
            print(f"Warning: Could not initialize ChromaDB: {e}")
            self.collection = None

    def search(
        self,
        query: str,
        carriers: Optional[List[str]] = None,
        document_types: Optional[List[str]] = None,
        num_results: int = 5
    ) -> str:
        """
        Search policy documents for relevant information.
        """
        # If ChromaDB not available or no documents indexed, return mock data
        if not self.collection or self._get_doc_count() == 0:
            return self._mock_search(query, carriers, document_types)

        # Build filter
        where_filter = None
        if carriers or document_types:
            conditions = []
            if carriers:
                conditions.append({"carrier": {"$in": carriers}})
            if document_types:
                conditions.append({"doc_type": {"$in": document_types}})

            if len(conditions) == 1:
                where_filter = conditions[0]
            else:
                where_filter = {"$and": conditions}

        # Query
        results = self.collection.query(
            query_texts=[query],
            n_results=num_results,
            where=where_filter
        )

        # Format results
        formatted = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else None

                formatted.append({
                    "carrier": metadata.get("carrier", "unknown"),
                    "carrier_display": self._carrier_display_name(metadata.get("carrier", "")),
                    "document": metadata.get("source", "unknown"),
                    "document_type": metadata.get("doc_type", "unknown"),
                    "section": metadata.get("section", ""),
                    "page": metadata.get("page"),
                    "relevance": round(1 - distance, 3) if distance else None,
                    "content": doc[:800] + "..." if len(doc) > 800 else doc
                })

        return json.dumps({
            "query": query,
            "filters": {
                "carriers": carriers,
                "document_types": document_types
            },
            "results_count": len(formatted),
            "results": formatted
        }, indent=2)

    def _mock_search(
        self,
        query: str,
        carriers: Optional[List[str]] = None,
        document_types: Optional[List[str]] = None
    ) -> str:
        """Return mock search results when no documents indexed."""

        # Mock data based on common queries
        mock_results = {
            "exclusion": [
                {
                    "carrier": "sunlife",
                    "carrier_display": "Sun Life",
                    "document": "Term Life Policy Contract",
                    "document_type": "policy",
                    "content": "Exclusions: Death resulting from suicide within 2 years of policy issue. Death while engaged in criminal activity. Death from war or act of war.",
                    "relevance": 0.92
                },
                {
                    "carrier": "manulife",
                    "carrier_display": "Manulife",
                    "document": "Term Life Policy Wording",
                    "document_type": "policy",
                    "content": "This policy does not cover death caused by: suicide within the first 24 months, participation in a criminal act, active duty in armed forces during war.",
                    "relevance": 0.89
                }
            ],
            "critical illness": [
                {
                    "carrier": "sunlife",
                    "carrier_display": "Sun Life",
                    "document": "Critical Illness Covered Conditions",
                    "document_type": "brochure",
                    "content": "Sun Life Critical Illness covers 26 conditions including: Cancer, Heart Attack, Stroke, Coronary Artery Bypass Surgery, Kidney Failure, Major Organ Transplant, Multiple Sclerosis, Paralysis...",
                    "relevance": 0.95
                },
                {
                    "carrier": "manulife",
                    "carrier_display": "Manulife",
                    "document": "Critical Illness Product Guide",
                    "document_type": "guide",
                    "content": "Manulife Critical Illness Insurance covers 25 conditions. Core coverage includes cancer, heart attack, stroke. Optional riders available for early-stage conditions.",
                    "relevance": 0.91
                }
            ],
            "waiting period": [
                {
                    "carrier": "sunlife",
                    "carrier_display": "Sun Life",
                    "document": "Disability Insurance Policy",
                    "document_type": "policy",
                    "content": "Elimination Period: Benefits begin after a 90-day waiting period from the date of disability. Shorter waiting periods (30, 60 days) available at higher premium.",
                    "relevance": 0.94
                }
            ]
        }

        # Find relevant mock results
        results = []
        query_lower = query.lower()
        for key, mock_data in mock_results.items():
            if key in query_lower:
                for item in mock_data:
                    if not carriers or item["carrier"] in carriers:
                        results.append(item)

        # Default results if no matches
        if not results:
            results = [{
                "carrier": "sunlife",
                "carrier_display": "Sun Life",
                "document": "General Policy Information",
                "document_type": "guide",
                "content": f"Search results for '{query}' would appear here. In production, this searches actual policy documents. Please index documents using scripts/index_documents.py",
                "relevance": 0.5
            }]

        return json.dumps({
            "query": query,
            "filters": {
                "carriers": carriers,
                "document_types": document_types
            },
            "results_count": len(results),
            "results": results,
            "note": "Mock results - run scripts/index_documents.py to enable real document search"
        }, indent=2)

    def index_document(self, filepath: Path, carrier: str):
        """Index a single document."""
        if not self.collection:
            print("ChromaDB not available")
            return

        try:
            from pypdf import PdfReader
        except ImportError:
            print("pypdf not installed")
            return

        reader = PdfReader(filepath)

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text or not text.strip():
                continue

            # Chunk text
            chunks = self._chunk_text(text, chunk_size=500, overlap=50)

            for chunk_idx, chunk in enumerate(chunks):
                doc_id = f"{carrier}:{filepath.stem}:p{page_num}:c{chunk_idx}"

                self.collection.add(
                    documents=[chunk],
                    metadatas=[{
                        "carrier": carrier,
                        "source": filepath.name,
                        "page": page_num,
                        "chunk": chunk_idx,
                        "doc_type": self._infer_doc_type(filepath.name)
                    }],
                    ids=[doc_id]
                )

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)

        return chunks

    def _infer_doc_type(self, filename: str) -> str:
        """Infer document type from filename."""
        fl = filename.lower()
        if "policy" in fl or "contract" in fl:
            return "policy"
        elif "brochure" in fl:
            return "brochure"
        elif "faq" in fl:
            return "faq"
        elif "guide" in fl:
            return "guide"
        elif "terms" in fl:
            return "terms"
        else:
            return "other"

    def _get_doc_count(self) -> int:
        """Get count of indexed documents."""
        if not self.collection:
            return 0
        try:
            return self.collection.count()
        except:
            return 0

    def _carrier_display_name(self, carrier: str) -> str:
        """Get display name for carrier."""
        names = {
            "sunlife": "Sun Life",
            "manulife": "Manulife",
            "canadalife": "Canada Life"
        }
        return names.get(carrier, carrier)
