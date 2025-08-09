import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
// MVP: single tool that takes a short symptom input and returns a comprehensive response
// by constructing a richer prompt and calling an LLM via OpenAI-compatible API.
const OpenAIModel = process.env.OPENAI_MODEL || "gpt-4o-mini";
const OpenAIBaseUrl = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
const OpenAIApiKey = process.env.OPENAI_API_KEY || "";
if (!OpenAIApiKey) {
    // eslint-disable-next-line no-console
    console.warn("Warning: OPENAI_API_KEY is not set. The tool will fail on first call.");
}
const ToolInput = z.object({
    query: z.string().min(1, "query is required"),
    userLocation: z
        .object({ lat: z.number(), lon: z.number() })
        .optional()
});
function buildPrompt({ query, userLocation }) {
    const locationText = userLocation
        ? `User location (approx): lat=${userLocation.lat}, lon=${userLocation.lon}.`
        : "User location not provided.";
    return (`You are a cautious, helpful medical assistant. Expand on the user's message and return ALL of the following sections as JSON.

Input: "${query}"
${locationText}

Requirements:
1) Clarify the user intent from the symptom(s).
2) Suggest over-the-counter medicine options (if appropriate), with generic names and typical dosage guidance. Include cautions and when NOT to take.
3) List nearest 5 chemist/medical stores based on the provided location (if location is available). If not available, output an empty array and a note that location was not provided. Each item should have: name, address (if unknown, use empty string), and a placeholder map link.
4) Suggest 3-5 home remedies with short rationales.
5) Provide 3-5 YouTube video links relevant to home remedies or general guidance (do not embed, just direct URLs).
6) Add red flags: list symptoms that require immediate medical attention.
7) Disclaimers: not a substitute for professional medical advice; consult a healthcare professional.

Return a single JSON object with exactly these keys:
{
  "intent": string,
  "otc_medicines": [{ "name": string, "dosage_guidance": string, "cautions": string }],
  "nearby_chemists": [{ "name": string, "address": string, "map_url": string }],
  "home_remedies": [{ "title": string, "rationale": string }],
  "videos": [string],
  "red_flags": [string],
  "disclaimers": [string]
}
Ensure valid JSON.`);
}
async function callOpenAI(prompt) {
    const resp = await fetch(`${OpenAIBaseUrl}/chat/completions`, {
        method: "POST",
        headers: {
            "content-type": "application/json",
            authorization: `Bearer ${OpenAIApiKey}`,
        },
        body: JSON.stringify({
            model: OpenAIModel,
            messages: [
                { role: "system", content: "You are a careful medical assistant. Always return valid JSON only." },
                { role: "user", content: prompt }
            ],
            temperature: 0.2,
            response_format: { type: "json_object" }
        })
    });
    if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`OpenAI API error: ${resp.status} ${resp.statusText} - ${text}`);
    }
    const data = await resp.json();
    const text = data.choices?.[0]?.message?.content ?? "";
    return JSON.parse(text);
}
async function main() {
    const server = new McpServer({
        name: "medical-mcp-server",
        version: "0.1.0",
        instructions: "Medical assistant MCP: expand user symptom into structured advice via LLM.",
    });
    server.registerTool("medical_assist", {
        title: "Medical Assistant",
        description: "Takes a short symptom input and returns structured advice, OTC suggestions, chemists, home remedies, and videos.",
        inputSchema: {
            query: z.string().min(1),
            userLocation: z.object({ lat: z.number(), lon: z.number() }).optional()
        },
    }, async ({ query, userLocation }) => {
        const prompt = buildPrompt({ query, userLocation });
        const result = await callOpenAI(prompt);
        // Return as text content with the JSON result
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    });
    const transport = new StdioServerTransport();
    await server.connect(transport);
}
main().catch((err) => {
    // eslint-disable-next-line no-console
    console.error(err);
    process.exit(1);
});
