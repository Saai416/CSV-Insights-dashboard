# AI Notes & Implementation Details

## Model Selection
We selected **Llama-3.3-70b-versatile** via Groq API for this project.

### Why Llama 3.3 70B?
- **Performance**: Comparable to GPT-4 class models for analytical tasks.
- **Speed**: Groq's LPU inference engine provides near-instant responses, crucial for a real-time dashboard experience.
- **Context Window**: Sufficient for handling summarized CSV data and conversation history.
- **Reliability**: Excellent instruction following for structured JSON output.

## Prompt Engineering Strategy

### Structured Output
We enforce strict JSON output from the LLM to ensure reliable parsing by the frontend.
```json
{
  "summary": "Executive summary string...",
  "key_trends": ["Trend 1", "Trend 2"],
  "outliers": ["Outlier 1"],
  "risks": ["Risk 1"],
  "recommendations": ["Rec 1", "Rec 2"]
}
```

### Data Summarization
Since raw CSVs can exceed context limits, we pre-process the data using Pandas to generate a semantic summary:
- Row/Column counts
- Data types per column
- Missing value statistics
- Statistical summary (mean, max, min) for numeric columns
- Sample data rows

This summary is then fed to the LLM, ensuring it "sees" the shape and content of the data without needing to process every single token.

## Error Handling & Fallbacks
- **JSON Parsing**: The system includes robust try/catch blocks to handle potential malformed JSON from the LLM (though rare with Llama 3).
- **Graceful Degradation**: If the LLM service is down, the dashboard still renders the data analysis sections (charts, tables) and shows a specific error for the AI insights portion.
