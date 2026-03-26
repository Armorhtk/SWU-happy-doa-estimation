const owner = process.env.GITHUB_OWNER || "your-github-username";
const projectName = "SWU-happy-doa-estimation";

const config = {
  title: "SWU Happy DOA Estimation",
  tagline: "3 周完成雷达 DOA 入门，10 周逐步建设完整课程",
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
  themes: [],
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
        { to: "/docs/course-roadmap", label: "课程路线", position: "left" },
        { to: "/docs/quickstart", label: "快速开始", position: "left" },
        { to: "/docs/doa-intro", label: "DOA 入门", position: "left" },
        { to: "/docs/traditional-methods", label: "传统方法（建设中）", position: "left" },
        { to: "/docs/deep-learning", label: "深度学习（建设中）", position: "left" },
        { to: "/docs/about", label: "关于项目", position: "left" },
        { href: `https://github.com/${owner}/${projectName}`, label: "GitHub", position: "right" },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          title: "学习入口",
          items: [
            { label: "课程路线", to: "/docs/course-roadmap" },
            { label: "快速开始", to: "/docs/quickstart" },
            { label: "DOA 入门", to: "/docs/doa-intro" },
          ],
        },
        {
          title: "建设状态",
          items: [
            { label: "传统方法", to: "/docs/traditional-methods" },
            { label: "深度学习", to: "/docs/deep-learning" },
            { label: "FAQ", to: "/docs/faq" },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} SWU-happy-doa-estimation`,
    },
  },
};

module.exports = config;