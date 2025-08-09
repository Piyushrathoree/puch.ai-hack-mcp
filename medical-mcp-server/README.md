# Medical MCP Server (MVP)

A minimal Model Context Protocol (MCP) server that turns short symptom inputs into structured medical guidance by prompting an LLM via an OpenAI-compatible API, then enriches with nearby chemists and YouTube embed links.

- Tool: `medical_assist`
  - Input: `{ "query": string, "userLocation"?: { "lat": number, "lon": number } }`
  - Output: JSON string with keys: `intent`, `otc_medicines`, `nearby_chemists`, `home_remedies`, `videos`, `red_flags`, `disclaimers`.
  - Behavior:
    - Expands the symptom into a richer prompt and requests JSON from the model.
    - Resolves `nearby_chemists` (max 5) using OpenStreetMap Overpass API when `userLocation` is provided.
    - Normalizes `videos` to include `url` and `embed_url` for simple embedding.

## Requirements
- Node.js >= 18
- `OPENAI_API_KEY` for an OpenAI-compatible endpoint (e.g., OpenAI or compatible providers).

## Environment Variables
- `OPENAI_API_KEY` (required): API key for the OpenAI-compatible endpoint.
- `OPENAI_MODEL` (optional, default `gpt-4o-mini`): Chat model name.
- `OPENAI_BASE_URL` (optional, default `https://api.openai.com/v1`): Base URL of the OpenAI-compatible API.

## Install & Run Locally
```bash
cd /workspace/medical-mcp-server
npm install
npm run dev
```
This starts the server using stdio transport. Connect using any MCP-compatible client (Puch.ai handles WhatsApp + MCP; no extra work here).

## MCP Client Configuration Example
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
- Output example shape:
```json
{
  "intent": "...",
  "otc_medicines": [{ "name": "...", "dosage_guidance": "...", "cautions": "..."}],
  "nearby_chemists": [{ "name": "...", "address": "...", "map_url": "..."}],
  "home_remedies": [{ "title": "...", "rationale": "..."}],
  "videos": [{ "url": "https://www.youtube.com/watch?v=...", "embed_url": "https://www.youtube.com/embed/..."}],
  "red_flags": ["..."],
  "disclaimers": ["..."]
}
```

## Notes
- Nearby chemists use Overpass API (OSM). If `userLocation` is not provided or Overpass is unavailable, an empty list is returned.
- Model is requested to output JSON; still, the server validates and normalizes.
- Always includes disclaimers; this is not medical advice.

## Development
- Build: `npm run build`

## License
MIT