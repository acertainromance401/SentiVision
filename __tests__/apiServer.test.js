const http = require("http");
const { createServer } = require("../src/api/server");

function request(port, method, path, body) {
  return new Promise((resolve, reject) => {
    const payload = body ? JSON.stringify(body) : null;
    const req = http.request(
      {
        hostname: "127.0.0.1",
        port,
        method,
        path,
        headers: payload
          ? {
              "Content-Type": "application/json",
              "Content-Length": Buffer.byteLength(payload)
            }
          : {}
      },
      (res) => {
        let raw = "";
        res.on("data", (chunk) => {
          raw += chunk;
        });
        res.on("end", () => {
          resolve({ statusCode: res.statusCode, body: raw, headers: res.headers });
        });
      }
    );

    req.on("error", reject);
    if (payload) {
      req.write(payload);
    }
    req.end();
  });
}

describe("api server", () => {
  let server;

  beforeAll(async () => {
    const instance = createServer();
    server = instance.server;
    await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  });

  afterAll(async () => {
    await new Promise((resolve) => server.close(resolve));
  });

  test("returns health payload", async () => {
    const port = server.address().port;
    const response = await request(port, "GET", "/health");
    const body = JSON.parse(response.body);

    expect(response.statusCode).toBe(200);
    expect(body.status).toBe("ok");
  });

  test("analyze endpoint returns emotion result", async () => {
    const port = server.address().port;
    const response = await request(port, "POST", "/analyze", {
      colors: [
        { hex: "#1E3A8A", weight: 0.6 },
        { hex: "#38BDF8", weight: 0.4 }
      ]
    });
    const body = JSON.parse(response.body);

    expect(response.statusCode).toBe(200);
    expect(typeof body.predictedEmotion).toBe("string");
    expect(typeof body.confidence).toBe("number");
  });

  test("metrics endpoint exposes counters", async () => {
    const port = server.address().port;
    const response = await request(port, "GET", "/metrics");

    expect(response.statusCode).toBe(200);
    expect(response.body).toContain("sentivision_requests_total");
    expect(response.body).toContain("sentivision_analyze_requests_total");
  });
});
