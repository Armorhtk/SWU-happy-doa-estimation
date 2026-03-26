import clsx from "clsx";
import Layout from "@theme/Layout";
import Link from "@docusaurus/Link";
import useBaseUrl from "@docusaurus/useBaseUrl";

import styles from "./index.module.css";

const highlights = [
  {
    title: "适合谁",
    body: "面向本校本科生与 Python 初学者设计，默认你还没有系统学过 DOA。",
  },
  {
    title: "V1 学完能做什么",
    body: "能搭好本地环境、跑通 ULA 入门实验，并理解角度、阵元数和间距对结果的影响。",
  },
  {
    title: "后续会扩展什么",
    body: "项目总共按 10 周路线推进，后续 7 周会补上传统超分辨率方法和基于 PyTorch 的深度学习部分。",
  },
];

export default function Home() {
  const radarUrl = useBaseUrl("/img/radar.svg");

  return (
    <Layout
      title="SWU Happy DOA Estimation"
      description="面向本科生的雷达 DOA 估计开源入门课程"
    >
      <main className={styles.page}>
        <section className={styles.hero}>
          <div className={styles.heroText}>
            <p className={styles.kicker}>Radar DOA for Undergraduates</p>
            <h1>3 周完成雷达 DOA 入门</h1>
            <p className={styles.subtitle}>
              从零基础起步，先跑通第一组阵列响应实验，再逐步进入 MUSIC 与深度学习 DOA。
            </p>
            <div className={styles.actions}>
              <Link className="button button--primary button--lg" to="/docs/quickstart">
                立即开始
              </Link>
              <Link className="button button--secondary button--lg" to="/docs/course-roadmap">
                查看课程路线
              </Link>
            </div>
          </div>
          <div className={styles.heroVisual}>
            <img src={radarUrl} alt="Radar illustration" className={styles.radar} />
          </div>
        </section>

        <section className={styles.grid}>
          {highlights.map((item) => (
            <article key={item.title} className={clsx(styles.card, "shadow--md")}>
              <h2>{item.title}</h2>
              <p>{item.body}</p>
            </article>
          ))}
        </section>

        <section className={styles.roadmap}>
          <div className={styles.roadmapText}>
            <h2>V1 只做一件事：把入门闭环打透</h2>
            <p>
              这个版本不会假装“已经讲完所有 DOA”。它只交付真正能学完的一条路径：
              环境配置、基础概念、第一份可运行代码、实验观察、练习与答案。
            </p>
          </div>
          <div className={styles.timeline}>
            <div>
              <span>第 1 周</span>
              <strong>环境与路线</strong>
            </div>
            <div>
              <span>第 2 周</span>
              <strong>DOA 入门实验</strong>
            </div>
            <div>
              <span>第 3 周</span>
              <strong>FAQ 与公开发布</strong>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
