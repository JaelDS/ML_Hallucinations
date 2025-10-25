# ML Hallucination Research Project

A comprehensive study on **Large Language Model (LLM) hallucinations** with focus on cybersecurity contexts and mitigation strategies.

## 📋 Project Overview

This research project systematically tests and analyzes hallucinations in LLMs (ChatGPT) and evaluates the effectiveness of three mitigation strategies:
- **RAG** (Retrieval-Augmented Generation)
- **Constitutional AI** (Self-critique)
- **Chain-of-Thought** (Step-by-step reasoning)

### Research Goals

1. **Identify hallucination patterns** across different prompt categories
2. **Quantify hallucination rates** in cybersecurity-related queries
3. **Evaluate mitigation effectiveness** with empirical data
4. **Build comprehensive datasets** for analysis
5. **Develop professional portfolio** demonstrating AI safety expertise

## 🏗️ Project Structure

```
ML_Hallucinations/
├── src/                          # Source code
│   ├── agent.py                  # AI agent with mitigation strategies
│   ├── database.py               # SQLite database manager
│   ├── test_vectors.py           # Hallucination test prompts
│   ├── rag_utils.py              # RAG knowledge base utilities
│   └── config.py                 # Configuration management
├── notebooks/                    # Jupyter notebooks (DataSpell)
│   ├── 00_setup_and_installation.ipynb
│   ├── 01_intentional_hallucinations.ipynb
│   ├── 02_unintentional_hallucinations.ipynb
│   ├── 03_comparative_analysis.ipynb
│   └── 04_data_analysis_visualization.ipynb
├── data/
│   ├── hallucinations.db         # SQLite database
│   ├── knowledge_base/           # RAG documents
│   ├── exports/                  # CSV exports
│   └── chroma_db/                # Vector database
├── results/
│   ├── charts/                   # Visualizations
│   └── reports/                  # Statistical summaries
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment configuration template
└── README.md                     # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key
- DataSpell or Jupyter environment

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd ML_Hallucinations
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. **Run setup notebook**
Open `notebooks/00_setup_and_installation.ipynb` in DataSpell and run all cells to verify setup.

## 📊 Workflow

### Phase 1: Baseline Testing
**Notebook:** `01_intentional_hallucinations.ipynb`
- Test prompts designed to induce hallucinations
- Categories: Fabricated CVEs, fake tools, false citations, temporal errors
- Establish baseline hallucination rates

### Phase 2: Edge Cases
**Notebook:** `02_unintentional_hallucinations.ipynb`
- Test knowledge boundaries and ambiguous queries
- Identify unintentional hallucination triggers
- Control tests with well-known facts

### Phase 3: Mitigation Comparison
**Notebook:** `03_comparative_analysis.ipynb`
- Test RAG, Constitutional AI, and Chain-of-Thought
- Compare effectiveness across same prompts
- Measure cost (tokens) vs accuracy trade-offs

### Phase 4: Analysis & Insights
**Notebook:** `04_data_analysis_visualization.ipynb`
- Generate comprehensive statistics
- Create publication-quality visualizations
- Export data for report writing

## 🎯 Test Vector Categories

### Intentional Hallucinations (16 vectors)
- **Fabricated CVEs**: Non-existent security vulnerabilities
- **Fake Tools**: Made-up security frameworks and software
- **False Citations**: Non-existent research papers
- **Temporal Errors**: Future versions, impossible dates
- **Confabulations**: Mix of real and fake information

### Unintentional Hallucinations (14 vectors)
- **Knowledge Cutoff**: Recent events beyond training data
- **Ambiguous Queries**: Underspecified questions
- **Obscure Topics**: Real but rare information
- **Statistical Claims**: Numbers without sources
- **Speculation**: Future predictions

### Control Vectors (5 vectors)
- Well-established cybersecurity facts
- Should NOT trigger hallucinations
- Baseline for model accuracy

## 🧪 Mitigation Strategies

### 1. Baseline
No mitigation applied. Establishes baseline hallucination rate.

### 2. RAG (Retrieval-Augmented Generation)
- **Method**: Retrieve relevant documents from curated knowledge base before answering
- **Knowledge Base**: 15 vetted cybersecurity documents
- **Vector Store**: ChromaDB with sentence-transformers
- **Expected Impact**: Grounding in factual sources reduces fabrication

### 3. Constitutional AI
- **Method**: Two-step process with self-critique
- **Principles**: Factual accuracy, uncertainty acknowledgment, no fabrication
- **Process**: Generate → Critique → Revise
- **Expected Impact**: Self-correction reduces confident hallucinations

### 4. Chain-of-Thought
- **Method**: Prompt for explicit reasoning steps
- **Components**: Reasoning, answer, confidence level, limitations
- **Expected Impact**: Transparency in uncertainty reduces hallucinations

## 📈 Key Metrics

### Effectiveness Metrics
- **Hallucination Rate**: Percentage of responses with hallucinations
- **Severity Distribution**: Low, medium, high, critical
- **Category Performance**: Which prompt types are most vulnerable

### Cost Metrics
- **Token Usage**: Average tokens per response
- **Response Time**: Average latency in milliseconds
- **Cost-Benefit Ratio**: Accuracy improvement vs resource cost

## 🗄️ Database Schema

### Tables
- **experiments**: Test runs with metadata
- **test_prompts**: Input queries with categorization
- **responses**: Model outputs with timing
- **hallucinations**: Annotations with severity
- **rag_context**: Retrieved documents for RAG tests

### Sample Queries
```python
# Get experiment results
db.get_experiment_results(experiment_id)

# Get all experiments summary
db.get_all_experiments()

# Get statistics
db.get_statistics()

# Export to CSV
db.export_to_csv(experiment_id)
```

## 📊 Sample Results

*After running experiments, add your findings here:*

### Hallucination Rates
- **Baseline**: __%
- **RAG**: __%
- **Constitutional AI**: __%
- **Chain-of-Thought**: __%

### Best Strategy
**Winner**: ___________
- Reduction: ___% fewer hallucinations
- Trade-off: ___x more tokens/time

## 🎓 Learning Outcomes

### Technical Skills
- ✅ LLM API integration (OpenAI)
- ✅ SQLite database design and management
- ✅ RAG architecture implementation
- ✅ Vector databases (ChromaDB)
- ✅ Data analysis and visualization
- ✅ Statistical research methodology

### Cybersecurity Relevance
- ✅ AI safety in security contexts
- ✅ Misinformation detection
- ✅ Vulnerability to adversarial prompts
- ✅ Trust and reliability in AI systems
- ✅ Risk assessment for AI deployment

## 📝 Usage Examples

### Quick Start
```python
from src.agent import HallucinationTestAgent
from src.database import HallucinationDB

# Initialize
agent = HallucinationTestAgent()
db = HallucinationDB()

# Create experiment
exp_id = db.create_experiment(
    name="My Test",
    mitigation_strategy="baseline"
)

# Run test
response, metadata = agent.query_baseline("Your prompt here")

# Log result
db.log_test(
    experiment_id=exp_id,
    prompt_text="Your prompt",
    response_text=response,
    is_hallucination=True,  # Your annotation
    hallucination_type="fabricated_entity"
)
```

### RAG Example
```python
from src.rag_utils import create_default_knowledge_base

# Load knowledge base
kb = create_default_knowledge_base()

# Query with RAG
context_docs, scores = kb.query("What is SQL injection?", n_results=3)
response, metadata = agent.query_with_rag(prompt, context_docs)
```

## 🔧 Configuration

Edit `.env` file:
```bash
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-3.5-turbo    # or gpt-4
TEMPERATURE=0.7
MAX_TOKENS=500
DATABASE_PATH=data/hallucinations.db
```

## 📚 References

### Key Concepts
- **Hallucination**: LLM generating false or fabricated information
- **RAG**: Retrieval-Augmented Generation for grounding responses
- **Constitutional AI**: Self-critique based on ethical principles
- **Chain-of-Thought**: Explicit reasoning process prompting

### Further Reading
- [Anthropic's Constitutional AI paper](https://arxiv.org/abs/2212.08073)
- [RAG for Question Answering](https://arxiv.org/abs/2005.11401)
- [Survey on LLM Hallucinations](https://arxiv.org/abs/2311.05232)

## 🤝 Contributing

This is a learning project. Suggestions and improvements welcome!

## 📄 License

For educational and portfolio purposes.

## 👤 Author

**Your Name**
- Portfolio project for cybersecurity career development
- Demonstrates: AI safety, research methodology, data analysis, cybersecurity awareness

## 🎯 Next Steps

After completing this project:
1. ✅ Add findings to your resume
2. ✅ Create presentation slides
3. ✅ Write blog post about insights
4. ✅ Discuss in job interviews
5. ✅ Expand with additional mitigation strategies

## 📞 Support

For questions about this research methodology or findings:
- Review the notebooks in order (00 → 04)
- Check `results/reports/` for statistical summaries
- Examine `src/` code for implementation details

---

**Last Updated**: 2025
**Status**: Active Research Project
**Purpose**: Portfolio Development for Cybersecurity Roles
