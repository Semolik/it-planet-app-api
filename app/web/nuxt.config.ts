export default defineNuxtConfig({
    modules: ["@nuxtjs/google-fonts", "nuxt-icon", "@nuxt/ui"],
    devtools: { enabled: true },
    ssr: false,
    app: {
        head: {
            title: "Frienda",
        },
    },
    googleFonts: {
        families: {
            Jost: true,
        },
        download: true,
    },
    colorMode: {
        preference: "light",
        fallback: "light",
    },
    runtimeConfig: {
        public: {
            apiBase:
                process.env.NODE_ENV === "development"
                    ? "http://localhost:8000"
                    : "",
        },
    },
});
