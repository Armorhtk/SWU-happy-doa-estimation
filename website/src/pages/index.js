import Layout from "@theme/Layout";
import Link from "@docusaurus/Link";
import HeroRadar from "../components/HeroRadar";

import styles from "./index.module.css";

export default function Home() {
  return (
    <Layout
      title="SWU Happy DOA Estimation"
      description="开源、阶梯式的雷达 DOA 估计教程，构建从经典算法到深度学习的完整知识链。"
    >
      <main className={styles.page}>
        <section className={styles.hero}>
          <div className={styles.heroText}>
            <p className={styles.kicker}>SWU-HAPPY-DOA-ESTIMATION</p>
            <h1 className={styles.title}>
              <span className={styles.titleAccent}>Show Me your Code</span>
              <span className={styles.titleMain}>用 DOA 开启你的科研初探</span>
            </h1>
            <p className={styles.subtitle}>
              开源、阶梯式的雷达DOA估计教程，构建从经典算法到深度学习的完整知识链。
            </p>
            <div className={styles.actions}>
              <Link className="button button--primary button--lg" to="/docs/preface">
                开始学习 →
              </Link>
            </div>
          </div>

          <div className={styles.heroVisual}>
            <div className={styles.visualGlow} />
            <div className={styles.visualCard}>
              <HeroRadar className={styles.radar} />
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
