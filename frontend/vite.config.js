
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, "..", "");
    const apiKey = env.AGENT_SENTINEL_API_KEY;

    return {
        envDir: "..",

        server: {
            host: "127.0.0.1",

            proxy: {
                "/api": {
                    target: "http://127.0.0.1:8000",
                    changeOrigin: true,

                    rewrite: (path) =>
                        path.replace(/^\/api/, ""),

                    configure: (proxy) => {
                        proxy.on("proxyReq", (proxyReq) => {
                            if (apiKey) {
                                proxyReq.setHeader(
                                    "X-API-Key",
                                    apiKey
                                );
                            }
                        });
                    }
                }
            }
        }
    };
});
