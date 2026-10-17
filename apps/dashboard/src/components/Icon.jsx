export default function Icon({ name, size = 18, ...props }) {
  let shape;

  switch (name) {
    case "activity":
      shape = <><path d="M3 12h4l3-8 5 16 3-8h3" /><path d="M21 12h1" /></>;
      break;
    case "arrow-up":
      shape = <><path d="M12 19V5" /><path d="m5 12 7-7 7 7" /></>;
      break;
    case "arrow-up-right":
      shape = <><path d="M7 17 17 7" /><path d="M8 7h9v9" /></>;
      break;
    case "calendar":
      shape = <><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M16 3v4M8 3v4M3 10h18" /></>;
      break;
    case "chart":
      shape = <><path d="M4 19V5M4 19h17" /><path d="m7 15 4-4 3 2 6-7" /></>;
      break;
    case "check":
      shape = <path d="m5 12 4 4L19 6" />;
      break;
    case "chevron-down":
      shape = <path d="m7 10 5 5 5-5" />;
      break;
    case "clock":
      shape = <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>;
      break;
    case "close":
      shape = <><path d="m6 6 12 12M18 6 6 18" /></>;
      break;
    case "external":
      shape = <><path d="M14 4h6v6M20 4l-9 9" /><path d="M18 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6" /></>;
      break;
    case "eye":
      shape = <><path d="M2.5 12s3.3-6 9.5-6 9.5 6 9.5 6-3.3 6-9.5 6-9.5-6-9.5-6Z" /><circle cx="12" cy="12" r="2.5" /></>;
      break;
    case "eye-off":
      shape = <><path d="m3 3 18 18M10.6 10.6a2 2 0 0 0 2.8 2.8" /><path d="M9.9 5.2A10 10 0 0 1 12 5c6.2 0 9.5 7 9.5 7a15 15 0 0 1-3 3.7M6.2 6.3C3.7 8.2 2.5 12 2.5 12s3.3 7 9.5 7a9 9 0 0 0 3-.5" /></>;
      break;
    case "globe":
      shape = <><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" /></>;
      break;
    case "grid":
      shape = <><rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" /><rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" /></>;
      break;
    case "info":
      shape = <><circle cx="12" cy="12" r="9" /><path d="M12 11v5M12 8h.01" /></>;
      break;
    case "layers":
      shape = <><path d="m12 3 9 5-9 5-9-5 9-5Z" /><path d="m3 12 9 5 9-5M3 16l9 5 9-5" /></>;
      break;
    case "lock":
      shape = <><rect x="4" y="10" width="16" height="11" rx="2" /><path d="M8 10V7a4 4 0 1 1 8 0v3M12 14v3" /></>;
      break;
    case "logout":
      shape = <><path d="M10 17l5-5-5-5M15 12H3" /><path d="M12 3h6a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-6" /></>;
      break;
    case "mail":
      shape = <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m4 7 8 6 8-6" /></>;
      break;
    case "menu":
      shape = <><path d="M4 7h16M4 12h16M4 17h16" /></>;
      break;
    case "shield":
      shape = <><path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z" /><path d="m9 12 2 2 4-4" /></>;
      break;
    case "sparkle":
      shape = <><path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3Z" /><path d="m19 15 .8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15Z" /></>;
      break;
    default:
      shape = null;
  }

  return (
    <svg
      aria-hidden="true"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      {shape}
    </svg>
  );
}
