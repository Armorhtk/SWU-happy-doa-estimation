const owner = process.env.GITHUB_OWNER || "your-github-username";
const projectName = "SWU-happy-doa-estimation";

const config = {
  title: "SWU Happy DOA Estimation",
  tagline: "Show Me your Code，用 DOA 开启你的科研初探",
  favicon: "img/radar.svg",
  url: process.env.DOCUSAURUS_URL || `https://${owner}.github.io`,
  baseUrl: process.env.DOCUSAURUS_BASE_URL || `/${projectName}/`,
  organizationName: owner,
  projectName,
  trailingSlash: false,
  onBrokenLinks: "throw",
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: "warn",
    },
  },
  i18n: {
    defaultLocale: "zh-Hans",
    locales: ["zh-Hans"],
  },
  themes: [
    [
      "@easyops-cn/docusaurus-search-local",
      {
        indexDocs: true,
        indexBlog: false,
        indexPages: false,
        docsDir: "../docs",
        docsRouteBasePath: "/docs",
        language: ["en", "zh"],
        hashed: true,
        explicitSearchResultPath: true,
        searchBarShortcut: true,
        searchBarShortcutHint: true,
        searchBarShortcutKeymap: "mod+k",
        searchBarPosition: "left",
      },
    ],
  ],
  presets: [
    [
      "classic",
      {
        docs: {
          path: "../docs",
          routeBasePath: "docs",
          sidebarPath: require.resolve("./sidebars.js"),
        },
        blog: false,
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      },
    ],
  ],
  themeConfig: {
    image: "img/social-card.svg",
    navbar: {
      title: "SWU Happy DOA",
      logo: {
        alt: "Radar icon",
        src: "img/radar.svg",
      },
      items: [
        {
          href: `https://github.com/${owner}/${projectName}`,
          label: "GitHub",
          position: "right",
        },
      ],
    },
    colorMode: {
      defaultMode: "light",
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    footer: {
      style: "dark",
      links: [],
      copyright: `Copyright © ${new Date().getFullYear()} SWU-happy-doa-estimation`,
    },
  },
};

module.exports = config;
