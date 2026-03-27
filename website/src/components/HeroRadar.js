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
          <stop offset="0%" stopColor="#14222b" />
          <stop offset="62%" stopColor="#111827" />
          <stop offset="100%" stopColor="#0b1220" />
        </radialGradient>
        <linearGradient id="hero-radar-beam" x1="50%" y1="50%" x2="100%" y2="50%">
          <stop offset="0%" stopColor="#f59e0b" stopOpacity="0" />
          <stop offset="72%" stopColor="#f59e0b" stopOpacity="0.12" />
          <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.5" />
        </linearGradient>
      </defs>

      <rect width="450" height="450" rx="18" fill="url(#hero-radar-surface)" />

      <circle cx="225" cy="225" r="68" fill="none" stroke="#374151" strokeWidth="1.2" opacity="0.34" />
      <circle cx="225" cy="225" r="135" fill="none" stroke="#374151" strokeWidth="1.2" opacity="0.34" />
      <circle cx="225" cy="225" r="202" fill="none" stroke="#374151" strokeWidth="1.2" opacity="0.34" />
      <line x1="225" y1="24" x2="225" y2="426" stroke="#374151" strokeWidth="1.2" opacity="0.34" />
      <line x1="24" y1="225" x2="426" y2="225" stroke="#374151" strokeWidth="1.2" opacity="0.34" />

      <circle cx="317" cy="95" r="4" fill="#f59e0b" opacity="0">
        <animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="1.4095s" repeatCount="indefinite" />
        <animate attributeName="r" values="0;4;8" dur="2s" begin="1.4095s" repeatCount="indefinite" />
      </circle>
      <circle cx="93" cy="277" r="4" fill="#f59e0b" opacity="0">
        <animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="0.7095s" repeatCount="indefinite" />
        <animate attributeName="r" values="0;4;8" dur="2s" begin="0.7095s" repeatCount="indefinite" />
      </circle>
      <circle cx="180" cy="117" r="4" fill="#f59e0b" opacity="0">
        <animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="0.7214s" repeatCount="indefinite" />
        <animate attributeName="r" values="0;4;8" dur="2s" begin="0.7214s" repeatCount="indefinite" />
      </circle>
      <circle cx="124" cy="200" r="4" fill="#f59e0b" opacity="0">
        <animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="1.3026s" repeatCount="indefinite" />
        <animate attributeName="r" values="0;4;8" dur="2s" begin="1.3026s" repeatCount="indefinite" />
      </circle>
      <circle cx="259" cy="178" r="4" fill="#f59e0b" opacity="0">
        <animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="0.2431s" repeatCount="indefinite" />
        <animate attributeName="r" values="0;4;8" dur="2s" begin="0.2431s" repeatCount="indefinite" />
      </circle>

      <g>
        <animateTransform
          attributeName="transform"
          type="rotate"
          from="0 225 225"
          to="360 225 225"
          dur="1.5s"
          repeatCount="indefinite"
        />
        <path d="M225 225 L428 124 A235 235 0 0 1 428 326 Z" fill="url(#hero-radar-beam)" opacity="0.85" />
        <line x1="225" y1="225" x2="428" y2="225" stroke="#f59e0b" strokeWidth="2.2" strokeLinecap="round" />
      </g>

      <circle cx="225" cy="225" r="4.5" fill="#ffffff" />
    </svg>
  );
}
