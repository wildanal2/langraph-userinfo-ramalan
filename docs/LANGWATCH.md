# LangWatch Integration Guide

## Overview

LangWatch telah diintegrasikan untuk memberikan **observability** dan **tracing** lengkap pada aplikasi chatbot. Ini memungkinkan monitoring real-time, debugging, dan analisis performa LLM calls.

## Features

✅ **Automatic LLM Tracing** - Semua LLM calls otomatis di-trace  
✅ **Session Tracking** - Track user sessions dengan session_id  
✅ **User Identification** - Identifikasi user berdasarkan email  
✅ **Metadata Enrichment** - Metadata lengkap (endpoint, user_data, completion status)  
✅ **Error Tracking** - Automatic error capture dan logging  
✅ **Environment Labels** - Pisahkan traces berdasarkan environment (dev/prod)  
✅ **Production Ready** - Toggle on/off via environment variable  

## Setup

### 1. Install Dependencies

```bash
make install
# atau
uv pip install langwatch
```

### 2. Get LangWatch API Key

1. Sign up di [https://langwatch.ai](https://langwatch.ai)
2. Create new project
3. Copy API key dari dashboard

### 3. Configure Environment

Tambahkan ke `.env`:

```env
# LangWatch Configuration
LANGWATCH_API_KEY=lw_xxxxxxxxxxxxx
LANGWATCH_ENDPOINT=https://app.langwatch.ai
LANGWATCH_ENABLED=true
```

**Production:**
```env
LANGWATCH_ENABLED=true
ENVIRONMENT=production
```

**Development:**
```env
LANGWATCH_ENABLED=true
ENVIRONMENT=development
```

**Disable (testing):**
```env
LANGWATCH_ENABLED=false
```

## What Gets Traced

### 1. LLM Calls
- Semua invoke, stream, extract_data, classify_intent
- Input prompts & output responses
- Token usage & latency
- Model information (Bedrock Nova)

### 2. Session Context
- `session_id` - Unique session identifier
- `user_id` - Email user (jika tersedia) atau session_id
- `labels` - Environment tag (development/production)

### 3. Metadata
- **Endpoint**: `start_message`, `chat_stream`
- **User State**: `is_returning`, `is_complete`
- **Data Collection**: `next_step`, `collected_fields`
- **User Message**: Input dari user
- **Errors**: Exception messages

### 4. LangGraph Workflow
- Node executions (chatbot, classifier, rag)
- State transitions
- Conditional routing decisions

## Trace Structure

```
Trace (session_id)
├── start_message
│   ├── LLM Call: Welcome message
│   └── Metadata: is_returning=false
│
├── chat_stream (message 1)
│   ├── LLM Call: Extract data
│   ├── LLM Call: Generate response
│   └── Metadata: next_step=nama, collected_fields=[]
│
├── chat_stream (message 2)
│   ├── LLM Call: Extract data
│   ├── LLM Call: Generate response
│   └── Metadata: next_step=kota, collected_fields=[nama]
│
└── chat_stream (final)
    ├── LLM Call: Fortune generation
    └── Metadata: is_complete=true, collected_fields=[nama,kota,...]
```

## Dashboard Views

### LangWatch Dashboard Features:

1. **Traces View**
   - Real-time trace list
   - Filter by session_id, user_id, labels
   - Search by metadata

2. **Trace Details**
   - Full conversation flow
   - LLM call details (input/output/tokens)
   - Timing & latency breakdown
   - Error stack traces

3. **Analytics**
   - Token usage per session
   - Average completion time
   - Success/error rates
   - User journey funnel

4. **Debugging**
   - Inspect failed sessions
   - Compare prompt variations
   - Identify bottlenecks

## Code Examples

### Manual Trace Update (Optional)

```python
import langwatch
from src.core.config import settings

# Update trace with custom metadata
if settings.langwatch_enabled:
    langwatch.get_current_trace().update(
        metadata={
            "custom_field": "value",
            "user_action": "clicked_fortune_button"
        }
    )
```

### Custom Span (Advanced)

```python
import langwatch

@langwatch.span(name="custom_operation")
def my_function():
    # Your code here
    pass
```

## Production Checklist

- [ ] Set `LANGWATCH_API_KEY` di production environment
- [ ] Set `LANGWATCH_ENABLED=true`
- [ ] Set `ENVIRONMENT=production`
- [ ] Verify traces muncul di dashboard
- [ ] Setup alerts untuk error rates
- [ ] Monitor token usage & costs
- [ ] Review trace retention policy

## Troubleshooting

### Traces tidak muncul

1. Check API key valid:
```bash
echo $LANGWATCH_API_KEY
```

2. Check logs:
```bash
# Should see: "LangWatch tracing initialized"
tail -f logs/app.log | grep -i langwatch
```

3. Verify enabled:
```python
from src.core.config import settings
print(settings.langwatch_enabled)  # Should be True
```

### High latency

LangWatch adds minimal overhead (~5-10ms per trace). Jika latency tinggi:
- Check network ke LangWatch endpoint
- Verify Redis performance
- Review LLM response times di dashboard

### Missing metadata

Pastikan trace context di-update sebelum LLM call:
```python
langwatch.get_current_trace().update(metadata={...})
result = llm_service.invoke(prompt)
```

## Cost Considerations

**LangWatch Pricing:**
- Free tier: 10K traces/month
- Pro: $49/month (100K traces)
- Enterprise: Custom pricing

**Estimasi usage:**
- 1 complete conversation = ~5-10 traces
- 1000 users/day = ~5K-10K traces/day
- Monthly: ~150K-300K traces

**Recommendation:**
- Development: Free tier OK
- Production (<3K users/day): Pro plan
- Production (>3K users/day): Enterprise

## Best Practices

1. **Use descriptive metadata**
   ```python
   metadata={
       "endpoint": "chat_stream",
       "user_intent": "asking_question",
       "data_completeness": "75%"
   }
   ```

2. **Tag environments**
   - Labels automatically include environment
   - Easy filtering: `label:production`

3. **Track user journeys**
   - Use consistent session_id
   - Include user_id when available

4. **Monitor errors**
   - Errors automatically captured
   - Set up alerts in LangWatch

5. **Review regularly**
   - Weekly: Check error rates
   - Monthly: Analyze token usage
   - Quarterly: Optimize prompts based on traces

## Security

- API keys stored in environment variables
- Traces include user data (nama, email) - ensure compliance
- PII masking available in LangWatch settings
- Data retention configurable (default 30 days)

## Support

- LangWatch Docs: https://docs.langwatch.ai
- LangWatch Discord: https://discord.gg/langwatch
- GitHub Issues: Report bugs di repo ini

## Next Steps

1. ✅ Install & configure LangWatch
2. ✅ Run application & verify traces
3. 📊 Explore dashboard & analytics
4. 🔍 Debug issues using traces
5. 📈 Optimize prompts based on insights
6. 🚨 Setup alerts & monitoring
