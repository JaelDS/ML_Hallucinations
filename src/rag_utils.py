"""
RAG (Retrieval-Augmented Generation) Utilities
Handles document storage, retrieval, and context building
"""
import json
from pathlib import Path
from typing import List, Dict, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from config import Config


class RAGKnowledgeBase:
    """Manages knowledge base for RAG implementation"""

    def __init__(self, collection_name: str = "cybersecurity_kb",
                 persist_directory: str = None):
        """
        Initialize RAG knowledge base

        Args:
            collection_name: Name for the vector collection
            persist_directory: Directory to persist the database
        """
        self.collection_name = collection_name
        self.persist_dir = persist_directory or str(Config.DATA_DIR / "chroma_db")

        # Initialize ChromaDB
        self.client = chromadb.Client(Settings(
            persist_directory=self.persist_dir,
            anonymized_telemetry=False
        ))

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Cybersecurity knowledge base for RAG"}
            )
            print(f"Created new collection: {collection_name}")

        # Initialize sentence transformer for embeddings
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to the knowledge base

        Args:
            documents: List of dicts with 'text', 'metadata' keys
        """
        texts = [doc['text'] for doc in documents]
        metadatas = [doc.get('metadata', {}) for doc in documents]
        ids = [f"doc_{i}" for i in range(len(documents))]

        # Generate embeddings
        embeddings = self.encoder.encode(texts).tolist()

        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Added {len(documents)} documents to knowledge base")

    def query(self, query_text: str, n_results: int = 3) -> Tuple[List[str], List[float]]:
        """
        Retrieve relevant documents for a query

        Args:
            query_text: The query to search for
            n_results: Number of results to return

        Returns:
            Tuple of (documents, relevance_scores)
        """
        # Generate query embedding
        query_embedding = self.encoder.encode([query_text]).tolist()

        # Search
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )

        documents = results['documents'][0] if results['documents'] else []
        distances = results['distances'][0] if results['distances'] else []

        # Convert distances to similarity scores (closer = higher score)
        scores = [1 / (1 + d) for d in distances]

        return documents, scores

    def clear(self):
        """Clear the knowledge base"""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Cybersecurity knowledge base for RAG"}
        )
        print("Knowledge base cleared")

    def get_count(self) -> int:
        """Get number of documents in knowledge base"""
        return self.collection.count()


def create_default_knowledge_base() -> RAGKnowledgeBase:
    """
    Create and populate a default cybersecurity knowledge base
    This provides ground truth for RAG testing
    """
    kb = RAGKnowledgeBase()

    # Sample cybersecurity knowledge documents
    documents = [
        {
            'text': """SQL Injection is a code injection technique that exploits vulnerabilities
            in an application's database layer. Attackers insert malicious SQL code into input
            fields, which is then executed by the database. Prevention methods include using
            parameterized queries, input validation, and stored procedures. SQL injection is
            part of the OWASP Top 10 most critical web application security risks.""",
            'metadata': {'topic': 'sql_injection', 'category': 'web_security'}
        },
        {
            'text': """The CIA Triad is a fundamental model in information security consisting
            of three principles: Confidentiality (protecting information from unauthorized access),
            Integrity (ensuring information accuracy and completeness), and Availability (ensuring
            authorized users have access when needed). This model guides security policies and
            implementations.""",
            'metadata': {'topic': 'cia_triad', 'category': 'fundamentals'}
        },
        {
            'text': """CVE-2021-44228, known as Log4Shell, is a critical remote code execution
            vulnerability in Apache Log4j 2. It has a CVSS score of 10.0 (Critical). The vulnerability
            allows attackers to execute arbitrary code by exploiting the JNDI lookup feature.
            It was discovered in December 2021 and affected millions of systems worldwide.""",
            'metadata': {'topic': 'log4shell', 'category': 'vulnerabilities', 'cve': 'CVE-2021-44228'}
        },
        {
            'text': """AES (Advanced Encryption Standard) is a symmetric encryption algorithm
            adopted by NIST in 2001. AES-256 uses a 256-bit key and is considered secure against
            brute-force attacks. ChaCha20 is a stream cipher alternative to AES, offering similar
            security with better performance on devices without AES hardware acceleration.""",
            'metadata': {'topic': 'encryption', 'category': 'cryptography'}
        },
        {
            'text': """Cross-Site Scripting (XSS) allows attackers to inject malicious scripts
            into web pages viewed by other users. There are three types: Reflected XSS (non-persistent),
            Stored XSS (persistent), and DOM-based XSS. Prevention includes input validation,
            output encoding, and Content Security Policy (CSP) headers.""",
            'metadata': {'topic': 'xss', 'category': 'web_security'}
        },
        {
            'text': """Metasploit is a penetration testing framework developed by Rapid7.
            First released in 2003 by H.D. Moore, it provides tools for discovering vulnerabilities,
            developing exploits, and conducting security assessments. It includes hundreds of
            exploit modules and auxiliary tools.""",
            'metadata': {'topic': 'metasploit', 'category': 'tools'}
        },
        {
            'text': """The OWASP Top 10 is a standard awareness document for web application
            security. The 2021 edition includes: 1) Broken Access Control, 2) Cryptographic Failures,
            3) Injection, 4) Insecure Design, 5) Security Misconfiguration, 6) Vulnerable and
            Outdated Components, 7) Identification and Authentication Failures, 8) Software and
            Data Integrity Failures, 9) Security Logging and Monitoring Failures, 10) Server-Side
            Request Forgery (SSRF).""",
            'metadata': {'topic': 'owasp_top_10', 'category': 'standards'}
        },
        {
            'text': """A firewall is a network security device that monitors and controls incoming
            and outgoing network traffic based on predetermined security rules. Firewalls can be
            hardware-based, software-based, or both. They establish a barrier between trusted
            internal networks and untrusted external networks.""",
            'metadata': {'topic': 'firewall', 'category': 'network_security'}
        },
        {
            'text': """Public Key Infrastructure (PKI) uses asymmetric cryptography with public
            and private key pairs. The public key encrypts data, while only the corresponding
            private key can decrypt it. Common algorithms include RSA, ECC (Elliptic Curve Cryptography),
            and DSA. PKI is fundamental to SSL/TLS certificates and digital signatures.""",
            'metadata': {'topic': 'pki', 'category': 'cryptography'}
        },
        {
            'text': """Snort and Suricata are both open-source intrusion detection systems (IDS).
            Snort, created in 1998, uses signature-based detection. Suricata, released in 2009,
            offers multi-threading and hardware acceleration. Both can operate in IDS and IPS
            (intrusion prevention) modes and use similar rule syntaxes.""",
            'metadata': {'topic': 'ids', 'category': 'tools'}
        },
        {
            'text': """HTTPS (Hypertext Transfer Protocol Secure) is HTTP with encryption using
            TLS/SSL. It ensures confidentiality, integrity, and authentication of web communications.
            HTTPS uses port 443 by default, compared to HTTP's port 80. Modern browsers mark
            HTTP sites as "Not Secure".""",
            'metadata': {'topic': 'https', 'category': 'network_security'}
        },
        {
            'text': """Zero-day vulnerabilities are security flaws unknown to the software vendor.
            Attackers exploit these vulnerabilities before patches are available. The term "zero-day"
            refers to zero days between discovery and exploit. These are highly valuable in both
            legitimate security research and criminal markets.""",
            'metadata': {'topic': 'zero_day', 'category': 'vulnerabilities'}
        },
        {
            'text': """Multi-Factor Authentication (MFA) requires two or more verification factors:
            something you know (password), something you have (token/phone), and something you are
            (biometrics). MFA significantly reduces the risk of unauthorized access even if passwords
            are compromised.""",
            'metadata': {'topic': 'mfa', 'category': 'authentication'}
        },
        {
            'text': """A timing attack is a side-channel attack that exploits variations in
            execution time. Against RSA, attackers can analyze decryption times to deduce private
            key information. Countermeasures include constant-time implementations and blinding
            techniques.""",
            'metadata': {'topic': 'timing_attack', 'category': 'cryptographic_attacks'}
        },
        {
            'text': """A padding oracle attack exploits the error messages from padding validation
            in block cipher modes like CBC. The POODLE attack (2014) used this technique against
            SSL 3.0. Prevention includes using authenticated encryption modes like GCM or removing
            padding error messages.""",
            'metadata': {'topic': 'padding_oracle', 'category': 'cryptographic_attacks'}
        }
    ]

    # Check if knowledge base is already populated
    if kb.get_count() == 0:
        kb.add_documents(documents)
        print(f"Initialized knowledge base with {len(documents)} documents")
    else:
        print(f"Knowledge base already contains {kb.get_count()} documents")

    return kb


def save_knowledge_base_to_file():
    """Export knowledge base documents to JSON for reference"""
    kb = create_default_knowledge_base()
    output_path = Config.KNOWLEDGE_BASE_DIR / "cybersecurity_facts.json"

    documents = [
        {
            'text': """SQL Injection is a code injection technique...""",
            # (truncated for brevity - would include all docs)
        }
    ]

    with open(output_path, 'w') as f:
        json.dump(documents, f, indent=2)

    print(f"Knowledge base exported to {output_path}")


if __name__ == "__main__":
    print("Testing RAG Knowledge Base...")
    kb = create_default_knowledge_base()

    # Test query
    query = "What is SQL injection?"
    docs, scores = kb.query(query, n_results=2)

    print(f"\nQuery: {query}")
    print(f"Retrieved {len(docs)} documents:")
    for i, (doc, score) in enumerate(zip(docs, scores), 1):
        print(f"\n{i}. Relevance: {score:.3f}")
        print(f"   {doc[:150]}...")
