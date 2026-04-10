const CENTER = 225;
const SWEEP_DURATION = 1.5;
const TARGETS = [
  { cx: 317, cy: 95 },
  { cx: 93, cy: 277 },
  { cx: 180, cy: 117 },
  { cx: 124, cy: 200 },
  { cx: 259, cy: 178 },
];

function getSweepPhase(cx, cy) {
  const angle = Math.atan2(cy - CENTER, cx - CENTER);
  const normalized = (angle + Math.PI * 2) % (Math.PI * 2);
  return normalized / (Math.PI * 2);
}

function toKeyTimes(phase) {
  const preHit = Math.max(0, phase - 0.026);
  const persistence = Math.min(0.985, phase + 0.098);
  const fadeOut = Math.min(0.998, phase + 0.182);
  return `0;${preHit.toFixed(4)};${phase.toFixed(4)};${persistence.toFixed(4)};${fadeOut.toFixed(4)};1`;
}

export default function HeroRadar({ className = "" }) {
  return (
    <svg
      className={className}
      viewBox="0 0 450 450"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="Animated radar sweep"
    >
      <defs>
        <radialGradient id="hero-radar-surface" cx="50%" cy="50%" r="75%">
          <stop offset="0%" stopColor="var(--hero-radar-surface-core)" />
          <stop offset="62%" stopColor="var(--hero-radar-surface-mid)" />
          <stop offset="100%" stopColor="var(--hero-radar-surface-edge)" />
        </radialGradient>
        <linearGradient id="hero-radar-beam" x1="50%" y1="50%" x2="100%" y2="50%">
          <stop offset="0%" stopColor="var(--hero-radar-beam-color)" stopOpacity="0" />
          <stop offset="72%" stopColor="var(--hero-radar-beam-color)" stopOpacity="0.12" />
          <stop offset="100%" stopColor="var(--hero-radar-beam-color)" stopOpacity="0.5" />
        </linearGradient>
      </defs>

      <rect width="450" height="450" rx="28" fill="url(#hero-radar-surface)" />

      <circle cx="225" cy="225" r="68" fill="none" stroke="var(--hero-radar-grid)" strokeWidth="1.2" opacity="0.34" />
      <circle cx="225" cy="225" r="135" fill="none" stroke="var(--hero-radar-grid)" strokeWidth="1.2" opacity="0.34" />
      <circle cx="225" cy="225" r="202" fill="none" stroke="var(--hero-radar-grid)" strokeWidth="1.2" opacity="0.34" />
      <line x1="225" y1="24" x2="225" y2="426" stroke="var(--hero-radar-grid)" strokeWidth="1.2" opacity="0.34" />
      <line x1="24" y1="225" x2="426" y2="225" stroke="var(--hero-radar-grid)" strokeWidth="1.2" opacity="0.34" />

      {TARGETS.map((target) => {
        const phase = getSweepPhase(target.cx, target.cy);
        const keyTimes = toKeyTimes(phase);

        return (
          <circle key={`${target.cx}-${target.cy}`} cx={target.cx} cy={target.cy} r="3" fill="var(--hero-radar-target)" opacity="0.04">
            <animate
              attributeName="opacity"
              values="0.04;0.04;1;0.34;0.12;0.04"
              keyTimes={keyTimes}
              dur={`${SWEEP_DURATION}s`}
              repeatCount="indefinite"
            />
            <animate
              attributeName="r"
              values="3;3;4.6;3.5;3.1;3"
              keyTimes={keyTimes}
              dur={`${SWEEP_DURATION}s`}
              repeatCount="indefinite"
            />
          </circle>
        );
      })}

      <g>
        <animateTransform
          attributeName="transform"
          type="rotate"
          from="0 225 225"
          to="360 225 225"
          dur={`${SWEEP_DURATION}s`}
          repeatCount="indefinite"
        />
        <path d="M225 225 L428 124 A235 235 0 0 1 428 326 Z" fill="url(#hero-radar-beam)" opacity="0.85" />
        <line x1="225" y1="225" x2="428" y2="225" stroke="var(--hero-radar-beam-color)" strokeWidth="2.2" strokeLinecap="round" />
      </g>

      <circle cx="225" cy="225" r="4.5" fill="var(--hero-radar-center)" />
    </svg>
  );
}
