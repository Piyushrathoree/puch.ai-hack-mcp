# puch-mcp-server (MVP)

Minimal MCP server exposing two web-focused tools:
- fetch_readable: Extract readable article content from a URL
- parse_rss: Parse an RSS/Atom feed

## Prereqs
- Node.js >= 18

## Install
```bash
cd /workspace/puch-mcp-server
npm install
```

## Develop
```bash
npm run dev
```

This uses stdio transport; run via an MCP-compatible client.

## Build
```bash
npm run build
```

## Configure (example for clients supporting server.json)
```json
{
  "mcpServers": {
    "puch-mcp-server": {
      "command": "node",
      "args": ["--enable-source-maps", "--no-warnings", "--loader", "tsx", "src/server.ts"],
      "env": {}
    }
  }
}
```

## Tools
- fetch_readable
  - input: { "url": string }
  - returns: JSON string with { url, title, byline, textContent, length }

- parse_rss
  - input: { "url": string, "maxItems"?: number }
  - returns: JSON string with { title, url, items: [{ title, link, isoDate }] }