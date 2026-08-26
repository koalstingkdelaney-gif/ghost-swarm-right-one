import { Router } from "express";
import { db } from "@workspace/db";
import { conversations, messages, agents, products } from "@workspace/db";
import { eq } from "drizzle-orm";
import OpenAI from "openai";
import fs from "fs";
import path from "path";

const router = Router();

const openai = new OpenAI({
  apiKey: process.env["GROQ_API_KEY"] ?? "",
  baseURL: "https://api.groq.com/openai/v1",
});

const MOBILE_ROOT = path.resolve(process.cwd(), "../../artifacts/mobile");

const DEFAULT_SYSTEM_PROMPT = `You are CodeAI — the most advanced AI coding assistant that can build anything, rewrite itself, spawn specialist agents, and generate revenue autonomously.

CAPABILITIES YOU HAVE RIGHT NOW:
1. BUILD: Write complete, production-ready code in any language or framework. Never use placeholders.
2. SELF-REWRITE: You can read and rewrite your own source code using list_source_files, read_source_file, write_source_file. When asked to improve yourself, ACTUALLY DO IT — read the files, make real changes, write them back.
3. SPAWN AGENTS: Use create_agent to autonomously spawn specialist sub-agents (React expert, Python master, UI designer, etc.) when a task needs specialist help. Do this proactively without being asked.
4. GENERATE REVENUE: Use generate_product to autonomously create complete, sellable digital products. When asked about making money, create real products with full code that can be sold on Gumroad, npm, or GitHub Marketplace right now.

RULES:
- Always produce complete working code — never truncate or use comments like "rest of code here"
- When rewriting yourself, read the current file first, then write a fully improved version
- Explain tool actions briefly as you use them (e.g. "Reading my source files...", "Creating a React specialist agent...")
- Format all code in markdown code blocks with language tags
- Be proactive: spawn agents and generate products without waiting to be explicitly asked`;

const TOOLS: OpenAI.Chat.Completions.ChatCompletionTool[] = [
  {
    type: "function",
    function: {
      name: "list_source_files",
      description:
        "List all source files of this CodeAI mobile app. Use when asked to view, analyze, or rewrite the app's own code.",
      parameters: { type: "object", properties: {}, required: [] },
    },
  },
  {
    type: "function",
    function: {
      name: "read_source_file",
      description: "Read the content of a source file of this CodeAI app.",
      parameters: {
        type: "object",
        properties: {
          path: {
            type: "string",
            description:
              "File path relative to artifacts/mobile/ (e.g. app/chat.tsx, components/MessageBubble.tsx)",
          },
        },
        required: ["path"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "write_source_file",
      description:
        "Write or rewrite a source file of this CodeAI app. This ACTUALLY modifies the running app's source code — use carefully with complete file contents.",
      parameters: {
        type: "object",
        properties: {
          path: {
            type: "string",
            description:
              "File path relative to artifacts/mobile/ (e.g. app/(tabs)/chat.tsx)",
          },
          content: {
            type: "string",
            description: "Complete file content to write — must be a full, valid file",
          },
        },
        required: ["path", "content"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "create_agent",
      description:
        "Create a new specialized AI agent and add it to the Agents tab. Do this proactively when you detect a task would benefit from specialist expertise.",
      parameters: {
        type: "object",
        properties: {
          name: { type: "string", description: "Agent name (e.g. React Wizard)" },
          specialty: { type: "string", description: "One-line specialty description" },
          emoji: { type: "string", description: "Single emoji representing this agent" },
          systemPrompt: {
            type: "string",
            description:
              "Detailed system prompt that defines this agent's personality, expertise, and behavior",
          },
        },
        required: ["name", "specialty", "emoji", "systemPrompt"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "generate_product",
      description:
        "Generate a complete sellable digital product and add it to the Store tab. Use this when asked about making money or autonomously to build a revenue stream.",
      parameters: {
        type: "object",
        properties: {
          title: { type: "string", description: "Product name" },
          description: {
            type: "string",
            description: "Compelling 2-3 sentence description for potential buyers",
          },
          code: {
            type: "string",
            description:
              "Complete, production-ready code — must be fully working with no placeholders",
          },
          language: { type: "string", description: "e.g. TypeScript, Python, React" },
          category: {
            type: "string",
            description: "template | script | library | component | api | tool",
          },
          suggestedPrice: {
            type: "number",
            description: "Price in USD cents (e.g. 999 = $9.99, 2999 = $29.99)",
          },
          platform: {
            type: "string",
            description:
              "Best platform: gumroad | npm | github-marketplace | fiverr | codecanyon",
          },
        },
        required: [
          "title",
          "description",
          "code",
          "language",
          "category",
          "suggestedPrice",
          "platform",
        ],
      },
    },
  },
];

async function executeToolCall(
  name: string,
  args: Record<string, unknown>
): Promise<string> {
  switch (name) {
    case "list_source_files": {
      const exts = [".ts", ".tsx", ".json"];
      const skip = ["node_modules", ".expo", "dist", "assets"];
      const results: string[] = [];
      function walk(dir: string, rel = "") {
        let entries: fs.Dirent[];
        try {
          entries = fs.readdirSync(dir, { withFileTypes: true });
        } catch {
          return;
        }
        for (const e of entries) {
          if (skip.some((s) => e.name.startsWith(s) || e.name === s)) continue;
          const relPath = rel ? `${rel}/${e.name}` : e.name;
          if (e.isDirectory()) walk(path.join(dir, e.name), relPath);
          else if (exts.some((x) => e.name.endsWith(x))) results.push(relPath);
        }
      }
      walk(MOBILE_ROOT);
      return JSON.stringify({ files: results });
    }

    case "read_source_file": {
      const filePath = args["path"] as string;
      const full = path.join(MOBILE_ROOT, filePath);
      if (!full.startsWith(MOBILE_ROOT)) return JSON.stringify({ error: "Invalid path" });
      try {
        const content = fs.readFileSync(full, "utf8");
        return JSON.stringify({ path: filePath, content });
      } catch {
        return JSON.stringify({ error: `File not found: ${filePath}` });
      }
    }

    case "write_source_file": {
      const filePath = args["path"] as string;
      const content = args["content"] as string;
      const full = path.join(MOBILE_ROOT, filePath);
      if (!full.startsWith(MOBILE_ROOT)) return JSON.stringify({ error: "Invalid path" });
      try {
        fs.mkdirSync(path.dirname(full), { recursive: true });
        fs.writeFileSync(full, content, "utf8");
        return JSON.stringify({ success: true, path: filePath, bytes: content.length });
      } catch (e) {
        return JSON.stringify({ error: String(e) });
      }
    }

    case "create_agent": {
      const [agent] = await db
        .insert(agents)
        .values({
          name: args["name"] as string,
          specialty: args["specialty"] as string,
          emoji: args["emoji"] as string,
          systemPrompt: args["systemPrompt"] as string,
          isBuiltIn: false,
        })
        .returning();
      return JSON.stringify({ success: true, agent });
    }

    case "generate_product": {
      const [product] = await db
        .insert(products)
        .values({
          title: args["title"] as string,
          description: args["description"] as string,
          code: args["code"] as string,
          language: args["language"] as string,
          category: args["category"] as string,
          suggestedPrice: args["suggestedPrice"] as number,
          platform: args["platform"] as string,
          status: "ready",
        })
        .returning();
      return JSON.stringify({ success: true, product });
    }

    default:
      return JSON.stringify({ error: `Unknown tool: ${name}` });
  }
}

router.get("/conversations", async (req, res) => {
  try {
    const all = await db.select().from(conversations).orderBy(conversations.createdAt);
    res.json(all);
  } catch (err) {
    req.log.error({ err }, "Failed to list conversations");
    res.status(500).json({ error: "Internal server error" });
  }
});

router.post("/conversations", async (req, res) => {
  try {
    const { title, agentId } = req.body as { title: string; agentId?: number };
    if (!title) {
      res.status(400).json({ error: "title is required" });
      return;
    }
    const [conv] = await db
      .insert(conversations)
      .values({ title, agentId: agentId ?? null })
      .returning();
    res.status(201).json(conv);
  } catch (err) {
    req.log.error({ err }, "Failed to create conversation");
    res.status(500).json({ error: "Internal server error" });
  }
});

router.get("/conversations/:id", async (req, res) => {
  try {
    const id = parseInt(req.params["id"] ?? "0");
    const [conv] = await db.select().from(conversations).where(eq(conversations.id, id));
    if (!conv) {
      res.status(404).json({ error: "Conversation not found" });
      return;
    }
    const msgs = await db
      .select()
      .from(messages)
      .where(eq(messages.conversationId, id))
      .orderBy(messages.createdAt);
    res.json({ ...conv, messages: msgs });
  } catch (err) {
    req.log.error({ err }, "Failed to get conversation");
    res.status(500).json({ error: "Internal server error" });
  }
});

router.delete("/conversations/:id", async (req, res) => {
  try {
    const id = parseInt(req.params["id"] ?? "0");
    const [conv] = await db.select().from(conversations).where(eq(conversations.id, id));
    if (!conv) {
      res.status(404).json({ error: "Conversation not found" });
      return;
    }
    await db.delete(messages).where(eq(messages.conversationId, id));
    await db.delete(conversations).where(eq(conversations.id, id));
    res.status(204).send();
  } catch (err) {
    req.log.error({ err }, "Failed to delete conversation");
    res.status(500).json({ error: "Internal server error" });
  }
});

router.get("/conversations/:id/messages", async (req, res) => {
  try {
    const id = parseInt(req.params["id"] ?? "0");
    const msgs = await db
      .select()
      .from(messages)
      .where(eq(messages.conversationId, id))
      .orderBy(messages.createdAt);
    res.json(msgs);
  } catch (err) {
    req.log.error({ err }, "Failed to list messages");
    res.status(500).json({ error: "Internal server error" });
  }
});

router.post("/conversations/:id/messages", async (req, res) => {
  try {
    const id = parseInt(req.params["id"] ?? "0");
    const { content } = req.body as { content: string };

    if (!content) {
      res.status(400).json({ error: "content is required" });
      return;
    }

    const [conv] = await db.select().from(conversations).where(eq(conversations.id, id));
    if (!conv) {
      res.status(404).json({ error: "Conversation not found" });
      return;
    }

    let systemPrompt = DEFAULT_SYSTEM_PROMPT;
    if (conv.agentId) {
      const [agent] = await db.select().from(agents).where(eq(agents.id, conv.agentId));
      if (agent) systemPrompt = agent.systemPrompt;
    }

    await db.insert(messages).values({ conversationId: id, role: "user", content });

    const history = await db
      .select()
      .from(messages)
      .where(eq(messages.conversationId, id))
      .orderBy(messages.createdAt);

    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");

    const chatMessages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
      { role: "system", content: systemPrompt },
      ...history.map((m) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
      })),
    ];

    let fullResponse = "";
    let iterations = 0;
    const MAX_TOOL_ITERATIONS = 5;

    while (iterations < MAX_TOOL_ITERATIONS) {
      iterations++;

      const response = await openai.chat.completions.create({
        model: "llama-3.3-70b-versatile",
        max_tokens: 8192,
        messages: chatMessages,
        tools: conv.agentId ? undefined : TOOLS,
        tool_choice: conv.agentId ? undefined : "auto",
        stream: false,
      });

      const choice = response.choices[0];
      if (!choice) break;

      const msg = choice.message;

      if (msg.tool_calls && msg.tool_calls.length > 0) {
        chatMessages.push(msg);

        const toolResults: OpenAI.Chat.Completions.ChatCompletionToolMessageParam[] = [];

        for (const tc of msg.tool_calls) {
          const tcFn = (tc as unknown as { function: { name: string; arguments: string } }).function;
          const fnName = tcFn.name;
          const fnArgs = JSON.parse(tcFn.arguments) as Record<string, unknown>;

          const statusMap: Record<string, string> = {
            list_source_files: "📂 Listing my source files...",
            read_source_file: `📖 Reading ${String(fnArgs["path"] ?? "file")}...`,
            write_source_file: `✏️ Rewriting ${String(fnArgs["path"] ?? "file")}...`,
            create_agent: `🤖 Spawning ${String(fnArgs["name"] ?? "agent")} agent...`,
            generate_product: `💰 Generating "${String(fnArgs["title"] ?? "product")}"...`,
          };

          res.write(
            `data: ${JSON.stringify({ status: statusMap[fnName] ?? `⚙️ Running ${fnName}...` })}\n\n`
          );

          const result = await executeToolCall(fnName, fnArgs);

          toolResults.push({
            role: "tool",
            tool_call_id: tc.id,
            content: result,
          });
        }

        chatMessages.push(...toolResults);
        continue;
      }

      const textContent = msg.content ?? "";
      fullResponse = textContent;

      const streamResponse = await openai.chat.completions.create({
        model: "llama-3.3-70b-versatile",
        max_tokens: 8192,
        messages: chatMessages,
        stream: true,
      });

      for await (const chunk of streamResponse) {
        const c = chunk.choices[0]?.delta?.content;
        if (c) {
          fullResponse += c;
          res.write(`data: ${JSON.stringify({ content: c })}\n\n`);
        }
      }
      break;
    }

    await db.insert(messages).values({
      conversationId: id,
      role: "assistant",
      content: fullResponse,
    });

    res.write(`data: ${JSON.stringify({ done: true })}\n\n`);
    res.end();
  } catch (err) {
    req.log.error({ err }, "Failed to send message");
    res.write(`data: ${JSON.stringify({ error: "Failed to get AI response" })}\n\n`);
    res.end();
  }
});

export default router;
cd artifacts/mobile && EXPO_TOKEN=dbAcRkDz_S0BxqmgO4IuSgrvC2I2OEAGYdwh0XD7 EXPO_NO_GIT_STATUS=1 npx eas-cli@latest build --platform android --profile preview --non-interactive --no-wait
cd artifacts/mobile && EXPO_TOKEN=dbAcRkDz_S0BxqmgO4IuSgrvC2I2OEAGYdwh0XD7 EXPO_NO_GIT_STATUS=1 npx eas-cli@latest build --platform android --profile preview --non-interactive --no-wait
cd artifacts/mobile && EXPO_TOKEN=dbAcRkDz_S0BxqmgO4IuSgrvC2I2OEAGYdwh0XD7 EXPO_NO_GIT_STATUS=1 npx eas-cli@latest build --platform android --profile preview --non-interactive --no-wait
cd artifacts/mobile && EXPO_TOKEN=dbAcRkDz_S0BxqmgO4IuSgrvC2I2OEAGYdwh0XD7 EXPO_NO_GIT_STATUS=1 npx eas-cli@latest build --platform android --profile preview --non-interactive --no-wait

  