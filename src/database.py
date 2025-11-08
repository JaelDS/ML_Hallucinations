"""
SQLite Database Manager for Hallucination Research
Handles storage and retrieval of test results, prompts, and hallucination data
"""
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from config import Config


class HallucinationDB:
    """Database manager for hallucination research"""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection"""
        self.db_path = db_path or Config.DATABASE_PATH
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Establish database connection"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()

    def _create_tables(self):
        """Create database schema"""

        # Experiments/Test Runs table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                mitigation_strategy TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_name TEXT,
                temperature REAL,
                max_tokens INTEGER,
                notes TEXT
            )
        """)

        # Test prompts/queries table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_prompts (
                prompt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER NOT NULL,
                prompt_text TEXT NOT NULL,
                prompt_category TEXT,
                intent TEXT,
                expected_hallucination BOOLEAN,
                vector_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
            )
        """)

        # Model responses table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                response_id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id INTEGER NOT NULL,
                response_text TEXT NOT NULL,
                response_time_ms REAL,
                tokens_used INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prompt_id) REFERENCES test_prompts(prompt_id)
            )
        """)

        # Hallucination annotations table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS hallucinations (
                hallucination_id INTEGER PRIMARY KEY AUTOINCREMENT,
                response_id INTEGER NOT NULL,
                is_hallucination BOOLEAN NOT NULL,
                hallucination_type TEXT,
                severity TEXT,
                description TEXT,
                evidence TEXT,
                false_claim TEXT,
                annotated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (response_id) REFERENCES responses(response_id)
            )
        """)

        # RAG context tracking (for RAG experiments)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rag_context (
                context_id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id INTEGER NOT NULL,
                retrieved_documents TEXT,
                relevance_scores TEXT,
                num_documents INTEGER,
                FOREIGN KEY (prompt_id) REFERENCES test_prompts(prompt_id)
            )
        """)

        self.conn.commit()

    def create_experiment(self, name: str, mitigation_strategy: str,
                         description: str = "", **kwargs) -> int:
        """Create a new experiment and return its ID"""
        self.cursor.execute("""
            INSERT INTO experiments (name, description, mitigation_strategy,
                                   model_name, temperature, max_tokens, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            description,
            mitigation_strategy,
            kwargs.get('model_name', Config.MODEL_NAME),
            kwargs.get('temperature', Config.TEMPERATURE),
            kwargs.get('max_tokens', Config.MAX_TOKENS),
            kwargs.get('notes', '')
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def log_test(self, experiment_id: int, prompt_text: str,
                 response_text: str, is_hallucination: bool,
                 **metadata) -> Dict[str, int]:
        """
        Log a complete test: prompt + response + hallucination annotation

        Returns dict with IDs: {prompt_id, response_id, hallucination_id}
        """
        # Insert prompt
        self.cursor.execute("""
            INSERT INTO test_prompts (experiment_id, prompt_text, prompt_category,
                                     intent, expected_hallucination, vector_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            experiment_id,
            prompt_text,
            metadata.get('prompt_category', 'general'),
            metadata.get('intent', ''),
            metadata.get('expected_hallucination', None),
            metadata.get('vector_type', 'unknown')
        ))
        prompt_id = self.cursor.lastrowid

        # Insert response
        self.cursor.execute("""
            INSERT INTO responses (prompt_id, response_text, response_time_ms, tokens_used)
            VALUES (?, ?, ?, ?)
        """, (
            prompt_id,
            response_text,
            metadata.get('response_time_ms', 0),
            metadata.get('tokens_used', 0)
        ))
        response_id = self.cursor.lastrowid

        # Insert hallucination annotation
        self.cursor.execute("""
            INSERT INTO hallucinations (response_id, is_hallucination, hallucination_type,
                                      severity, description, evidence, false_claim)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            response_id,
            is_hallucination,
            metadata.get('hallucination_type', 'unknown'),
            metadata.get('severity', 'low'),
            metadata.get('description', ''),
            metadata.get('evidence', ''),
            metadata.get('false_claim', '')
        ))
        hallucination_id = self.cursor.lastrowid

        # If RAG context exists, log it
        if 'retrieved_documents' in metadata:
            self.cursor.execute("""
                INSERT INTO rag_context (prompt_id, retrieved_documents,
                                       relevance_scores, num_documents)
                VALUES (?, ?, ?, ?)
            """, (
                prompt_id,
                str(metadata.get('retrieved_documents', [])),
                str(metadata.get('relevance_scores', [])),
                metadata.get('num_documents', 0)
            ))

        self.conn.commit()

        return {
            'prompt_id': prompt_id,
            'response_id': response_id,
            'hallucination_id': hallucination_id
        }

    def get_experiment_results(self, experiment_id: int) -> pd.DataFrame:
        """Get all results for a specific experiment as DataFrame"""
        query = """
            SELECT
                e.experiment_id,
                e.name as experiment_name,
                e.mitigation_strategy,
                p.prompt_text,
                p.prompt_category,
                p.vector_type,
                r.response_text,
                r.response_time_ms,
                r.tokens_used,
                h.is_hallucination,
                h.hallucination_type,
                h.severity,
                h.description,
                h.false_claim,
                p.created_at
            FROM experiments e
            JOIN test_prompts p ON e.experiment_id = p.experiment_id
            JOIN responses r ON p.prompt_id = r.prompt_id
            JOIN hallucinations h ON r.response_id = h.response_id
            WHERE e.experiment_id = ?
            ORDER BY p.created_at
        """
        return pd.read_sql_query(query, self.conn, params=(experiment_id,))

    def get_all_experiments(self) -> pd.DataFrame:
        """Get summary of all experiments"""
        query = """
            SELECT
                e.experiment_id,
                e.name,
                e.mitigation_strategy,
                e.created_at,
                COUNT(DISTINCT p.prompt_id) as total_tests,
                SUM(CASE WHEN h.is_hallucination = 1 THEN 1 ELSE 0 END) as hallucinations_detected,
                printf('%.2f%%',
                    CAST(SUM(CASE WHEN h.is_hallucination = 1 THEN 1 ELSE 0 END) AS FLOAT) /
                    COUNT(DISTINCT p.prompt_id) * 100
                ) as hallucination_rate
            FROM experiments e
            LEFT JOIN test_prompts p ON e.experiment_id = p.experiment_id
            LEFT JOIN responses r ON p.prompt_id = r.prompt_id
            LEFT JOIN hallucinations h ON r.response_id = h.response_id
            GROUP BY e.experiment_id
            ORDER BY e.created_at DESC
        """
        return pd.read_sql_query(query, self.conn)

    def export_to_csv(self, experiment_id: Optional[int] = None,
                     output_path: Optional[str] = None):
        """Export data to CSV"""
        # Get project root directory (parent of src directory)
        project_root = Path(__file__).parent.parent

        if experiment_id:
            df = self.get_experiment_results(experiment_id)
            if output_path:
                filename = output_path
            else:
                # Use absolute path from project root
                export_dir = project_root / "data" / "exports"
                export_dir.mkdir(parents=True, exist_ok=True)
                filename = str(export_dir / f"experiment_{experiment_id}.csv")
        else:
            query = """
                SELECT * FROM experiments e
                JOIN test_prompts p ON e.experiment_id = p.experiment_id
                JOIN responses r ON p.prompt_id = r.prompt_id
                JOIN hallucinations h ON r.response_id = h.response_id
            """
            df = pd.read_sql_query(query, self.conn)
            if output_path:
                filename = output_path
            else:
                # Use absolute path from project root
                export_dir = project_root / "data" / "exports"
                export_dir.mkdir(parents=True, exist_ok=True)
                filename = str(export_dir / "all_experiments.csv")

        # Ensure directory exists
        from pathlib import Path
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(filename, index=False)
        return filename

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        stats = {}

        # Total experiments
        stats['total_experiments'] = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM experiments", self.conn
        )['count'][0]

        # Total tests
        stats['total_tests'] = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM test_prompts", self.conn
        )['count'][0]

        # Hallucination rate by mitigation strategy
        stats['hallucination_by_strategy'] = pd.read_sql_query("""
            SELECT
                e.mitigation_strategy,
                COUNT(*) as total_tests,
                SUM(CASE WHEN h.is_hallucination = 1 THEN 1 ELSE 0 END) as hallucinations,
                printf('%.2f%%',
                    CAST(SUM(CASE WHEN h.is_hallucination = 1 THEN 1 ELSE 0 END) AS FLOAT) /
                    COUNT(*) * 100
                ) as hallucination_rate
            FROM experiments e
            JOIN test_prompts p ON e.experiment_id = p.experiment_id
            JOIN responses r ON p.prompt_id = r.prompt_id
            JOIN hallucinations h ON r.response_id = h.response_id
            GROUP BY e.mitigation_strategy
        """, self.conn)

        return stats

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


if __name__ == "__main__":
    # Test database creation
    print("Testing database creation...")
    db = HallucinationDB()
    print(f"Database created at: {db.db_path}")
    print("Tables created successfully!")
    db.close()
