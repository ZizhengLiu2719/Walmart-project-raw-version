import path from "path";
import Fastify from "fastify";
import mercurius from "mercurius";
import { fileURLToPath } from "url";
import { loadFilesSync } from "@graphql-tools/load-files";
import { mergeTypeDefs } from "@graphql-tools/merge";
import { print } from "graphql";
import type { FastifyRequest } from "fastify";
import { Resolvers, type AppContext } from "./resolvers/GraphqlResolver.js";

// load schema.graphql as string (ESM-safe)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = Number(process.env.PORT ?? 4000);

async function start() {
  const fastify = Fastify({ logger: true });

  const schema = buildSchemaSDL(); // DocumentNode acceptable to mercurius

  await fastify.register(mercurius, {
    schema,
    resolvers: Resolvers,
    graphiql: true,
    context: (request: FastifyRequest) => {
      const requestId =
        (request.headers["x-request-id"] as string) ?? undefined;
      return { requestId } as AppContext;
    },
  });

  fastify.get("/health", async (req, reply) => {
    return reply.code(200).send({ status: "ok", uptime: process.uptime() });
  });

  await fastify.listen({ port: PORT, host: "0.0.0.0" });
  fastify.log.info(`ready — http://localhost:${PORT}/graphql?graphiql=1`);
}
start().catch((err) => {
  console.error(err);
  process.exit(1);
});

function buildSchemaSDL(): string {
  // loads .graphql files synchronously and merges them into a DocumentNode
  const files = loadFilesSync(path.join(__dirname, "schemas"), {
    extensions: ["graphql"],
  });
  const merged = mergeTypeDefs(files); // DocumentNode | string
  // Convert DocumentNode -> SDL string (print is safe if merged is DocumentNode)
  const sdl = typeof merged === "string" ? merged : print(merged);
  return sdl;
}
