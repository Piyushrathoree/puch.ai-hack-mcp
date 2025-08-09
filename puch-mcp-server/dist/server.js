import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { Readability } from "@mozilla/readability";
import { JSDOM } from "jsdom";
import RSSParser from "rss-parser";
import pLimit from "p-limit";
const limit = pLimit(5);
async function fetchText(url) {
    const response = await fetch(url, { headers: { "user-agent": "puch-mcp-server/0.1" } });
    if (!response.ok) {
        throw new Error(`Failed to fetch ${url}: ${response.status} ${response.statusText}`);
    }
    return await response.text();
}
async function main() {
    const server = new McpServer({
        name: "puch-mcp-server",
        version: "0.1.0",
        instructions: "MVP web helper: parse readable content and RSS feeds.",
    });
    server.registerTool("fetch_readable", {
        title: "Fetch Readable Article",
        description: "Fetch a web page and extract readable article content (title, byline, text, length).",
        inputSchema: { url: z.string().url() },
    }, async ({ url }) => {
        const html = await limit(() => fetchText(url));
        const dom = new JSDOM(html, { url });
        const reader = new Readability(dom.window.document);
        const article = reader.parse();
        const payload = {
            url,
            title: article?.title ?? null,
            byline: article?.byline ?? null,
            textContent: article?.textContent ?? null,
            length: article?.textContent?.length ?? 0,
        };
        return { content: [{ type: "text", text: JSON.stringify(payload, null, 2) }] };
    });
    server.registerTool("parse_rss", {
        title: "Parse RSS/Atom",
        description: "Parse an RSS/Atom feed and return items with title, link, isoDate. Optional maxItems (default 10, max 50).",
        inputSchema: {
            url: z.string().url(),
            maxItems: z.number().int().min(1).max(50).optional(),
        },
    }, async ({ url, maxItems }) => {
        const parser = new RSSParser();
        const feed = await limit(() => parser.parseURL(url));
        const items = (feed.items ?? [])
            .slice(0, maxItems ?? 10)
            .map((i) => ({ title: i.title ?? "", link: i.link ?? "", isoDate: i.isoDate ?? null }));
        const payload = { title: feed.title ?? null, url, items };
        return { content: [{ type: "text", text: JSON.stringify(payload, null, 2) }] };
    });
    const transport = new StdioServerTransport();
    await server.connect(transport);
}
main().catch((err) => {
    // eslint-disable-next-line no-console
    console.error(err);
    process.exit(1);
});
