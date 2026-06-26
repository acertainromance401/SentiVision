const http = require("http");
const { analyzePaletteEmotion } = require("./aiService");

function createMetrics() {
  return {
    requestsTotal: 0,
    analyzeRequestsTotal: 0,
    analyzeErrorsTotal: 0,
    responseMsSum: 0,
    responseMsCount: 0,
    startedAtMs: Date.now()
  };
}

function jsonResponse(res, statusCode, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Content-Type": "application/json",
    "Content-Length": Buffer.byteLength(body)
  });
  res.end(body);
}

function textResponse(res, statusCode, body, contentType) {
  res.writeHead(statusCode, {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Content-Type": contentType,
    "Content-Length": Buffer.byteLength(body)
  });
  res.end(body);
}

function readJsonBody(req) {
  return new Promise((resolve, reject) => {
    let raw = "";

    req.on("data", (chunk) => {
      raw += chunk;
      if (raw.length > 1_000_000) {
        reject(new Error("Payload too large"));
      }
    });

    req.on("end", () => {
      if (!raw) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(raw));
      } catch {
        reject(new Error("Invalid JSON body"));
      }
    });

    req.on("error", reject);
  });
}

function toPrometheusMetrics(metrics) {
  const uptimeSeconds = Math.floor((Date.now() - metrics.startedAtMs) / 1000);
  return [
    "# HELP sentivision_requests_total Total HTTP requests",
    "# TYPE sentivision_requests_total counter",
    `sentivision_requests_total ${metrics.requestsTotal}`,
    "# HELP sentivision_analyze_requests_total Total analyze requests",
    "# TYPE sentivision_analyze_requests_total counter",
    `sentivision_analyze_requests_total ${metrics.analyzeRequestsTotal}`,
    "# HELP sentivision_analyze_errors_total Total analyze request errors",
    "# TYPE sentivision_analyze_errors_total counter",
    `sentivision_analyze_errors_total ${metrics.analyzeErrorsTotal}`,
    "# HELP sentivision_response_duration_ms_sum Sum of response durations in milliseconds",
    "# TYPE sentivision_response_duration_ms_sum counter",
    `sentivision_response_duration_ms_sum ${metrics.responseMsSum.toFixed(3)}`,
    "# HELP sentivision_response_duration_ms_count Number of measured response durations",
    "# TYPE sentivision_response_duration_ms_count counter",
    `sentivision_response_duration_ms_count ${metrics.responseMsCount}`,
    "# HELP sentivision_uptime_seconds Process uptime in seconds",
    "# TYPE sentivision_uptime_seconds gauge",
    `sentivision_uptime_seconds ${uptimeSeconds}`,
    ""
  ].join("\n");
}

function createServer(options = {}) {
  const metrics = options.metrics || createMetrics();
  const now = options.now || (() => Date.now());

  const server = http.createServer(async (req, res) => {
    const requestStart = now();
    metrics.requestsTotal += 1;

    const done = (statusCode) => {
      const duration = now() - requestStart;
      metrics.responseMsSum += duration;
      metrics.responseMsCount += 1;
      const line = {
        time: new Date().toISOString(),
        method: req.method,
        path: req.url,
        status: statusCode,
        durationMs: Number(duration.toFixed(2))
      };
      console.log(JSON.stringify(line));
    };

    if (req.method === "OPTIONS") {
      res.writeHead(204, {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
      });
      res.end();
      done(204);
      return;
    }

    if (req.method === "GET" && req.url === "/") {
      jsonResponse(res, 200, {
        service: "SentiVision AI API",
        endpoints: ["GET /health", "GET /metrics", "POST /analyze"]
      });
      done(200);
      return;
    }

    if (req.method === "GET" && req.url === "/health") {
      jsonResponse(res, 200, {
        status: "ok",
        service: "sentivision-ai-api",
        uptimeSeconds: Math.floor((Date.now() - metrics.startedAtMs) / 1000)
      });
      done(200);
      return;
    }

    if (req.method === "GET" && req.url === "/metrics") {
      const body = toPrometheusMetrics(metrics);
      textResponse(res, 200, body, "text/plain; version=0.0.4");
      done(200);
      return;
    }

    if (req.method === "POST" && req.url === "/analyze") {
      metrics.analyzeRequestsTotal += 1;
      try {
        const payload = await readJsonBody(req);
        const result = analyzePaletteEmotion(payload);
        jsonResponse(res, 200, result);
        done(200);
      } catch (error) {
        metrics.analyzeErrorsTotal += 1;
        jsonResponse(res, 400, {
          error: "bad_request",
          message: error.message
        });
        done(400);
      }
      return;
    }

    jsonResponse(res, 404, { error: "not_found" });
    done(404);
  });

  return { server, metrics };
}

function startServer(port = Number(process.env.PORT) || 8080) {
  const { server } = createServer();
  server.listen(port, "0.0.0.0", () => {
    console.log(JSON.stringify({ event: "server_started", port }));
  });
  return server;
}

if (require.main === module) {
  startServer();
}

module.exports = {
  createServer,
  startServer,
  toPrometheusMetrics
};
