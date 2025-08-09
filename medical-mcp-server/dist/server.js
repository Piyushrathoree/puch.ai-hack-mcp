import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
const OpenAIModel = process.env.OPENAI_MODEL || "gpt-4o-mini";
const OpenAIBaseUrl = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
const OpenAIApiKey = process.env.OPENAI_API_KEY || "";
if (!OpenAIApiKey) {
    // eslint-disable-next-line no-console
    console.warn("Warning: OPENAI_API_KEY is not set. The tool will fail on first call.");
}
const ToolInput = z.object({
    query: z.string().min(1, "query is required"),
    userLocation: z.object({ lat: z.number(), lon: z.number() }).optional(),
});
function youtubeEmbedUrl(rawUrl) {
    try {
        const url = new URL(rawUrl);
        let id = "";
        if (url.hostname.includes("youtu.be")) {
            id = url.pathname.replace(/^\//, "");
        }
        else if (url.hostname.includes("youtube.com")) {
            if (url.pathname.startsWith("/watch")) {
                id = url.searchParams.get("v") || "";
            }
            else if (url.pathname.startsWith("/embed/")) {
                id = url.pathname.split("/").pop() || "";
            }
            else if (url.pathname.startsWith("/shorts/")) {
                id = url.pathname.split("/")[2] || "";
            }
        }
        if (!id)
            return rawUrl;
        return `https://www.youtube.com/embed/${id}`;
    }
    catch {
        return rawUrl;
    }
}
function buildPrompt({ query }) {
    return (`You are a cautious, helpful medical assistant. Expand on the user's message and return ALL of the following sections as JSON.

Input: "${query}"

Requirements:
1) Clarify the user intent from the symptom(s).
2) Suggest over-the-counter medicine options (if appropriate), with generic names and typical dosage guidance. Include cautions and when NOT to take.
3) The server will supply nearby chemists separately; set "nearby_chemists" to an empty array.
4) Suggest 3-5 home remedies with short rationales.
5) Provide 3-5 YouTube video links relevant to home remedies or general guidance; return as array of objects with a "url" field only (the server will build embed URLs).
6) Add red flags: list symptoms that require immediate medical attention.
7) Disclaimers: not a substitute for professional medical advice; consult a healthcare professional.

Return a single JSON object with exactly these keys:
{
  "intent": string,
  "otc_medicines": [{ "name": string, "dosage_guidance": string, "cautions": string }],
  "nearby_chemists": [],
  "home_remedies": [{ "title": string, "rationale": string }],
  "videos": [{ "url": string }],
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
                { role: "user", content: prompt },
            ],
            temperature: 0.2,
            response_format: { type: "json_object" },
        }),
    });
    if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`OpenAI API error: ${resp.status} ${resp.statusText} - ${text}`);
    }
    const data = await resp.json();
    const text = data.choices?.[0]?.message?.content ?? "";
    return JSON.parse(text);
}
function haversineMeters(lat1, lon1, lat2, lon2) {
    const toRad = (d) => (d * Math.PI) / 180;
    const R = 6371000;
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}
async function findNearbyChemists(lat, lon, limit = 5) {
    const radiusMeters = 3000;
    const query = `
[out:json][timeout:10];
(
  node["amenity"="pharmacy"](around:${radiusMeters},${lat},${lon});
  way["amenity"="pharmacy"](around:${radiusMeters},${lat},${lon});
  relation["amenity"="pharmacy"](around:${radiusMeters},${lat},${lon});
);
out center tags;`;
    const resp = await fetch("https://overpass-api.de/api/interpreter", {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ data: query }),
    });
    if (!resp.ok) {
        return [];
    }
    const data = await resp.json();
    const elements = data.elements || [];
    const withCoords = elements
        .map((el) => {
        const center = el.center || (el.lat && el.lon ? { lat: el.lat, lon: el.lon } : undefined);
        if (!center)
            return undefined;
        const tags = el.tags || {};
        const name = tags.name || "Pharmacy";
        const addressParts = [tags["addr:housenumber"], tags["addr:street"], tags["addr:city"], tags["addr:postcode"]].filter(Boolean);
        const address = addressParts.join(", ");
        const dist = haversineMeters(lat, lon, center.lat, center.lon);
        const map_url = `https://www.openstreetmap.org/?mlat=${center.lat}&mlon=${center.lon}#map=18/${center.lat}/${center.lon}`;
        return { name, address, map_url, dist };
    })
        .filter(Boolean);
    withCoords.sort((a, b) => a.dist - b.dist);
    return withCoords.slice(0, limit).map(({ name, address, map_url }) => ({ name, address, map_url }));
}
function normalizeVideos(v) {
    if (!Array.isArray(v))
        return [];
    const items = [];
    for (const item of v) {
        if (typeof item === "string") {
            items.push({ url: item, embed_url: youtubeEmbedUrl(item) });
        }
        else if (item && typeof item.url === "string") {
            items.push({ url: item.url, embed_url: youtubeEmbedUrl(item.url) });
        }
    }
    return items.slice(0, 5);
}
function coerceOutput(modelObj) {
    const payload = {
        intent: typeof modelObj?.intent === "string" ? modelObj.intent : "",
        otc_medicines: Array.isArray(modelObj?.otc_medicines)
            ? modelObj.otc_medicines.map((m) => ({
                name: String(m?.name || ""),
                dosage_guidance: String(m?.dosage_guidance || ""),
                cautions: String(m?.cautions || ""),
            }))
            : [],
        nearby_chemists: Array.isArray(modelObj?.nearby_chemists) ? [] : [], // will be filled later if coords provided
        home_remedies: Array.isArray(modelObj?.home_remedies)
            ? modelObj.home_remedies.map((h) => ({
                title: String(h?.title || ""),
                rationale: String(h?.rationale || ""),
            }))
            : [],
        videos: normalizeVideos(modelObj?.videos),
        red_flags: Array.isArray(modelObj?.red_flags) ? modelObj.red_flags.map((x) => String(x)) : [],
        disclaimers: Array.isArray(modelObj?.disclaimers) ? modelObj.disclaimers.map((x) => String(x)) : [],
    };
    return payload;
}
async function main() {
    const server = new McpServer({
        name: "medical-mcp-server",
        version: "0.1.0",
        instructions: "Medical assistant MCP: expand user symptom into structured advice via LLM.",
    });
    server.registerTool("medical_assist", {
        title: "Medical Assistant",
        description: "Takes a short symptom input and returns structured advice, OTC suggestions, nearby chemists (limit 5), home remedies, and YouTube links with embeds.",
        inputSchema: {
            query: z.string().min(1),
            userLocation: z.object({ lat: z.number(), lon: z.number() }).optional(),
        },
    }, async ({ query, userLocation }) => {
        // Ask model for everything except nearby chemists
        const prompt = buildPrompt({ query, userLocation });
        const modelObj = await callOpenAI(prompt);
        let payload = coerceOutput(modelObj);
        // Fill nearby chemists from Overpass if location provided
        if (userLocation) {
            try {
                const list = await findNearbyChemists(userLocation.lat, userLocation.lon, 5);
                payload.nearby_chemists = list;
            }
            catch {
                payload.nearby_chemists = [];
            }
        }
        else {
            payload.nearby_chemists = [];
        }
        // Return only the specified keys
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
