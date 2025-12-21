# LangWatch Quick Start - 5 Menit

## Setup Cepat

### 1. Install LangWatch (30 detik)
```bash
make install-langwatch
```

### 2. Dapatkan API Key (2 menit)
1. Buka https://langwatch.ai
2. Sign up / Login
3. Create new project → "Krea Chatbot"
4. Copy API key (format: `lw_xxxxxxxxxxxxx`)

### 3. Configure Environment (30 detik)
```bash
# Tambahkan ke .env
echo "LANGWATCH_API_KEY=lw_xxxxxxxxxxxxx" >> .env
echo "LANGWATCH_ENABLED=true" >> .env
```

### 4. Verify Setup (30 detik)
```bash
make verify-langwatch
```

### 5. Test Integration (1 menit)
```bash
# Run test script
python scripts/test_langwatch.py

# Atau test dengan aplikasi
make run-dev
```

### 6. View Traces (30 detik)
1. Buka https://app.langwatch.ai
2. Select project "Krea Chatbot"
3. View traces dari test

## ✅ Done!

LangWatch sekarang aktif dan melacak semua LLM calls.

## What's Being Traced?

✅ Semua LLM invocations (Bedrock Nova)  
✅ LangGraph workflow executions  
✅ Data extraction & intent classification  
✅ User sessions & conversations  
✅ Errors & exceptions  

## Dashboard Features

- **Real-time traces**: Lihat setiap conversation flow
- **Token usage**: Monitor costs per session
- **Latency metrics**: P50/P95/P99 response times
- **Error tracking**: Debug failed requests
- **User journeys**: Analyze completion rates

## Production Deployment

```env
# Production .env
ENVIRONMENT=production
LANGWATCH_ENABLED=true
LANGWATCH_API_KEY=lw_prod_xxxxxxxxxxxxx
```

## Disable Tracing

```env
LANGWATCH_ENABLED=false
```

## Troubleshooting

**Traces tidak muncul?**
```bash
# Check configuration
make verify-langwatch

# Check logs
tail -f logs/app.log | grep -i langwatch
```

**API key error?**
- Verify key format: `lw_xxxxxxxxxxxxx`
- Check key di dashboard: https://app.langwatch.ai/settings

## Dokumentasi Lengkap

- **Integration Guide**: `docs/LANGWATCH.md`
- **Production Deployment**: `docs/PRODUCTION_DEPLOYMENT.md`
- **Full Summary**: `LANGWATCH_INTEGRATION.md`

## Support

- LangWatch Docs: https://docs.langwatch.ai
- Discord: https://discord.gg/langwatch
- Email: support@langwatch.ai
