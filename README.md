# 🎓 AI Learning & Study Assistant

A terminal-based AI study assistant built in pure Python. It reads course
notes, answers student questions using a lightweight RAG (Retrieval-Augmented
Generation) style search, generates quizzes, builds day-wise study plans,
and remembers each student's history — all backed by simple JSON files.

## ✨ Features

- 📚 **Study materials**: notes stored as plain text in `knowledge_base/`
- 🤖 **Q&A**: ask a question about a course and get the most relevant notes back
- 📝 **Quiz generator**: interactive multiple-choice quizzes, auto-graded
- 📅 **Study planner**: spreads a course's topics across N days
- 🧠 **Memory**: every student's history, quiz scores, and plans are saved in JSON
- 🔎 **RAG-style search**: TF/cosine-similarity search over the knowledge base — no external ML libraries needed
- 🛠️ **Tool-based design**: quiz, study-plan, and search each live in their own "tool" module
- 💾 **All data in JSON**: `data/*.json` — no database required
- 💻 **Terminal UI**: simple numbered menu, runs anywhere Python 3 runs

## 📁 Project Structure

```
ai_learning_study_assistant/
│
├── main.py                    # terminal entry point / menu loop
├── requirements.txt
├── README.md
│
├── data/                      # all persistent JSON data
│   ├── students.json
│   ├── courses.json
│   ├── materials.json
│   ├── quiz_data.json
│   └── study_plans.json
│
├── knowledge_base/            # source notes used by the RAG search
│   ├── python.txt
│   ├── java.txt
│   ├── database.txt
│   └── ai_ml.txt
│
├── agent/
│   ├── assistant.py           # orchestrator: ties memory + rag + tools together
│   ├── memory.py              # student profiles / history (JSON-backed)
│   └── rag.py                 # TF/cosine-similarity retrieval engine
│
├── tools/
│   ├── quiz_tool.py           # interactive quiz runner
│   ├── study_plan_tool.py     # day-wise study plan generator
│   └── search_tool.py         # formats RAG results into an answer
│
└── utils/
    └── json_handler.py        # load_json / save_json helpers
```

## ▶️ How to run

No external packages are required — just Python 3.8+.

```bash
cd ai_learning_study_assistant
python main.py
```

You'll be asked for a student ID (used to save/load your profile), and then
you'll see a menu:

```
1. View available courses
2. Ask a question (search study material)
3. Take a quiz
4. Generate a study plan
5. View my progress
6. Exit
```

## 🧩 How the RAG search works

1. Each `knowledge_base/*.txt` file is split into paragraph-level "chunks".
2. Every chunk becomes a bag-of-words term-frequency vector.
3. Your question is converted into the same kind of vector.
4. Cosine similarity ranks the chunks against your question.
5. The best matching chunk(s) are shown as the answer.

This keeps the project dependency-free while still demonstrating the core
retrieval idea behind RAG. If you want to upgrade it later, `agent/rag.py`
is the only file you'd need to swap out — e.g. to call a real embeddings
API or an LLM.

## 💾 Data files

| File | Purpose |
|---|---|
| `data/students.json` | student profiles, history, quiz scores, study plans |
| `data/courses.json` | course names, topics, difficulty |
| `data/materials.json` | maps each course to its knowledge base file |
| `data/quiz_data.json` | question bank per course |
| `data/study_plans.json` | all generated study plans (keyed by plan id) |

## 🔧 Extending the project

- Add a new course: add an entry to `data/courses.json`, a matching
  `knowledge_base/<course>.txt` file, and questions in `data/quiz_data.json`.
- Swap in a real LLM: edit `agent/rag.py` and/or `tools/search_tool.py` to
  call the Anthropic API (or any provider) instead of / in addition to the
  cosine-similarity search.
- Add new tools: drop a new module into `tools/` and wire it up in
  `agent/assistant.py`.
