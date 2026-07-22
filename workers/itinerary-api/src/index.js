import seed from './seed.json';
import { handleRequest } from './app.js';

export default {
  async fetch(request, env, _ctx) {
    return handleRequest(request, {
      ...env,
      SEED_DOC: env.SEED_DOC || seed,
    });
  },
};
