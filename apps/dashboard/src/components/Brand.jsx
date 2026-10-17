export default function Brand({ light = false, compact = false }) {
  return (
    <span className={`brand${light ? " brand-light" : ""}${compact ? " brand-compact" : ""}`}>
      <span className="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 36 36" fill="none">
          <path d="M8 9.5 18 5l10 4.5v10L18 31 8 19.5v-10Z" />
          <path d="m8 9.5 10 5 10-5M18 14.5V31" />
          <circle cx="18" cy="14.5" r="2.1" />
        </svg>
      </span>
      {!compact && (
        <span className="brand-wordmark">
          <strong>NEXO</strong>
          <span>ANALYTICS</span>
        </span>
      )}
    </span>
  );
}
