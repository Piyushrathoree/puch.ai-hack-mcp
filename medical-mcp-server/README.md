# Medical MCP Server (MVP)

A minimal Model Context Protocol (MCP) server that turns short symptom inputs into structured medical guidance by prompting an LLM via an OpenAI-compatible API.

- Tool: `medical_assist`
  - Input: `{ "query": string, "userLocation"?: { "lat": number, "lon": number } }`
  - Output: JSON string with keys: `intent`, `otc_medicines`, `nearby_chemists`, `home_remedies`, `videos`, `red_flags`, `disclaimers`.
  - Behavior: Expands the symptom into a richer prompt, requests a JSON-object reply from the model, and returns the model’s JSON as text.

## Why this design
- Keep server logic tiny: instruct the model to produce exactly what Puch needs, and let Puch handle channels (e.g., WhatsApp) and MCP plumbing.
- Fully stateless: no DB; all state lives in the prompt + client.

## Requirements
- Node.js >= 18
- An API key for an OpenAI-compatible endpoint (e.g., OpenAI, compatible providers).

## Environment Variables
- `OPENAI_API_KEY` (required): API key for the OpenAI-compatible endpoint.
- `OPENAI_MODEL` (optional, default `gpt-4o-mini`): Chat model name.
- `OPENAI_BASE_URL` (optional, default `https://api.openai.com/v1`): Base URL of the OpenAI-compatible API.

Example `.env` file (if your runtime loads it):
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
```

## Install & Run Locally
```bash
cd /workspace/medical-mcp-server
npm install
npm run dev
```
This starts the server using stdio transport. Connect using any MCP-compatible client.

## MCP Client Configuration Example
For clients that support a `server.json` style config:
```json
{
  "mcpServers": {
    "medical-mcp-server": {
      "command": "node",
      "args": ["--enable-source-maps", "--no-warnings", "--loader", "tsx", "src/server.ts"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "OPENAI_MODEL": "gpt-4o-mini",
        "OPENAI_BASE_URL": "https://api.openai.com/v1"
      }
    }
  }
}
```

## Tool Contract
- Name: `medical_assist`
- Input:
```json
{
  "query": "i have fever",
  "userLocation": { "lat": 28.6139, "lon": 77.2090 }
}
```
- Output: One JSON string with exactly these keys:
```json
{
  "intent": "...",
  "otc_medicines": [{ "name": "...", "dosage_guidance": "...", "cautions": "..."}],
  "nearby_chemists": [{ "name": "...", "address": "...", "map_url": "..."}],
  "home_remedies": [{ "title": "...", "rationale": "..."}],
  "videos": ["https://www.youtube.com/..."],
  "red_flags": ["..."],
  "disclaimers": ["..."]
}
```
Note: The server requests JSON mode from the model, but downstream should still validate the JSON.

## Puch.ai Integration
- Puch.ai handles WhatsApp and MCP connections.
- Point Puch.ai to this server command and provide environment variables.
- The server returns only the structured content specified above; no extra chatter.

## Development
- Build: `npm run build`
- Lint/tests: not included in MVP; keep server small and focused.

## Security & Safety (MVP notes)
- This server does not diagnose; it provides general guidance with disclaimers and red flags.
- Always include a disclaimer in outputs.
- Do not store user data; avoid PII.

## License
MIT