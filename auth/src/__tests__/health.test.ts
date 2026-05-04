import { describe, it } from 'node:test';
import { equal } from 'node:assert';
import http from 'node:http';

describe('Auth health endpoint', () => {
  const startHealthServer = (poolMock) => {
    return new Promise((resolve) => {
      const server = http.createServer(async (req, res) => {
        if (req.url === '/health' && req.method === 'GET') {
          try {
            const client = await poolMock.connect();
            try {
              await Promise.race([
                client.query('SELECT 1'),
                new Promise((_, reject) => setTimeout(() => reject(new Error('DB timeout')), 2000)),
              ]);
            } finally {
              client.release();
            }
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ status: 'ok', db: 'reachable' }));
          } catch {
            res.writeHead(503, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ status: 'error', db: 'unreachable' }));
          }
          return;
        }
        res.writeHead(404);
        res.end();
      });
      server.listen(0, '0.0.0.0', () => {
        const addr = server.address();
        const port = typeof addr === 'object' && addr ? addr.port : 0;
        resolve({ port, close: () => server.close() });
      });
    });
  };

  const makeRequest = (port) => {
    return new Promise((resolve) => {
      const req = http.get(`http://localhost:${port}/health`, (res) => {
        let body = '';
        res.on('data', (chunk) => { body += chunk; });
        res.on('end', () => {
          resolve({ status: res.statusCode, body });
        });
      });
      req.on('error', () => resolve({ status: 0, body: '' }));
    });
  };

  it('returns 200 with db=reachable when pool.connect succeeds', async () => {
    const mockClient = {
      query: async () => ({ rows: [{ 1: 1 }] }),
      release: () => {},
    };
    const poolMock = {
      connect: async () => mockClient,
    };

    const { port, close } = await startHealthServer(poolMock);
    const { status, body } = await makeRequest(port);
    close();

    equal(status, 200);
    equal(body, '{"status":"ok","db":"reachable"}');
  });

  it('returns 503 with db=unreachable when pool.connect throws', async () => {
    const poolMock = {
      connect: async () => { throw new Error('connection refused'); },
    };

    const { port, close } = await startHealthServer(poolMock);
    const { status, body } = await makeRequest(port);
    close();

    equal(status, 503);
    equal(body, '{"status":"error","db":"unreachable"}');
  });

  it('returns 503 with db=unreachable when query times out', async () => {
    const mockClient = {
      query: async () => {
        await new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 3000));
      },
      release: () => {},
    };
    const poolMock = {
      connect: async () => mockClient,
    };

    const { port, close } = await startHealthServer(poolMock);
    const { status, body } = await makeRequest(port);
    close();

    equal(status, 503);
    equal(body, '{"status":"error","db":"unreachable"}');
  });
});