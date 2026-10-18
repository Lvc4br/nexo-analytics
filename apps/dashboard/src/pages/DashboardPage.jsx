import { useEffect, useMemo, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import Brand from "../components/Brand";
import Icon from "../components/Icon";
import { ApiError, getOverview, hasSession, logout } from "../lib/api";

const numberFormat = new Intl.NumberFormat("pt-BR");
const decimalFormat = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 });

function formatChange(value) {
  if (value === null) return "Sem base de comparação";
  if (value === 0) return "Sem variação";
  return `${value > 0 ? "+" : "−"}${decimalFormat.format(Math.abs(value))}%`;
}

function formatDate(value, options = {}) {
  return new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC", ...options }).format(new Date(`${value}T12:00:00Z`));
}

function pageTitle(path) {
  if (path === "/") return "Início";
  if (path === "/work") return "Projetos";
  return path;
}

function formatDuration(seconds) {
  if (seconds === null || seconds === undefined) return "—";
  const value = Math.max(0, Math.round(seconds));
  const minutes = Math.floor(value / 60);
  const remaining = value % 60;
  return minutes ? `${minutes} min ${remaining} s` : `${remaining} s`;
}

function breakdownLabel(name, kind) {
  const labels = {
    desktop: "Computador", mobile: "Celular", tablet: "Tablet",
    "samsung internet": "Samsung Internet", chrome: "Chrome", chromium: "Chromium",
    firefox: "Firefox", safari: "Safari", edge: "Edge", opera: "Opera",
    windows: "Windows", macos: "macOS", ios: "iOS", android: "Android",
    linux: "Linux", chromeos: "ChromeOS", unknown: "Não identificado",
  };
  if (kind === "region") {
    const [country, region] = name.split("-");
    try {
      const countryName = new Intl.DisplayNames(["pt-BR"], { type: "region" }).of(country) || country;
      return region ? `${countryName} · ${region}` : countryName;
    } catch {
      return name;
    }
  }
  return labels[name.toLowerCase()] || name;
}

function BreakdownPanel({ title, kind, items, emptyMessage }) {
  const source = items[0]?.source;
  return (
    <article className="panel breakdown-panel">
      <div className="panel-heading compact-heading">
        <div><span className="panel-overline">PÚBLICO</span><h2>{title}</h2></div>
        <span className="small-count">{source === "vercel" ? "VERCEL" : source === "nexo" ? "NEXO" : "SEM DADOS"}</span>
      </div>
      {items.length ? <div className="breakdown-list">
        {items.slice(0, 6).map((item) => (
          <div className="breakdown-row" key={item.name}>
            <span className="breakdown-name">{breakdownLabel(item.name, kind)}</span>
            <span className="breakdown-count"><strong>{numberFormat.format(item.pageviews)}</strong><small>{numberFormat.format(item.visitors)} {source === "vercel" ? "visitantes agregados" : "sessões"}</small></span>
          </div>
        ))}
      </div> : <p className="breakdown-empty">{emptyMessage}</p>}
      {kind === "device" && <p className="breakdown-note">No Nexo, a contagem representa sessões por categoria; ela não identifica aparelhos físicos nem deduplica o mesmo aparelho entre sessões.</p>}
      {kind === "region" && <p className="breakdown-note">Localização aproximada por país e, quando disponível no proxy confiável, região. Não é uma localização precisa.</p>}
    </article>
  );
}

function chartGeometry(values) {
  const width = 800;
  const height = 236;
  const padding = 12;
  const max = Math.max(...values, 0);
  const scale = max || 1;
  const points = values.map((value, index) => {
    const x = values.length <= 1 ? width : (index / (values.length - 1)) * width;
    const y = height - padding - (value / scale) * (height - padding * 2);
    return [x, y];
  });
  const line = points.map(([x, y], index) => `${index === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");
  const area = points.length ? `${line} L${width} ${height} L0 ${height} Z` : "";
  return { line, area, max };
}

export default function DashboardPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [days, setDays] = useState(30);
  const [refreshKey, setRefreshKey] = useState(0);
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setErrorMessage("");
    getOverview(days)
      .then((result) => { if (!cancelled) setOverview(result); })
      .catch((error) => {
        if (cancelled) return;
        if (error instanceof ApiError && error.status === 401) {
          logout();
          navigate("/login", { replace: true });
          return;
        }
        setErrorMessage(error instanceof ApiError ? error.message : "Não foi possível carregar as métricas.");
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [days, navigate, refreshKey]);

  const chart = useMemo(() => chartGeometry(overview?.traffic.map((day) => day.pageviews) ?? []), [overview]);
  const chartTicks = chart.max ? [1, 0.75, 0.5, 0.25, 0].map((fraction) => Math.round(chart.max * fraction)) : [0, 0, 0, 0, 0];
  const dateTicks = overview?.traffic.filter((_, index, items) => {
    const positions = [0, Math.floor((items.length - 1) / 3), Math.floor(((items.length - 1) * 2) / 3), items.length - 1];
    return positions.includes(index);
  }) ?? [];

  if (!hasSession()) return <Navigate to="/login" replace />;

  function leaveDashboard() {
    logout();
    navigate("/login", { replace: true });
  }

  const metrics = overview ? [
    { label: "Visualizações de página", value: numberFormat.format(overview.metrics.pageviews), change: overview.comparison.pageviews_percent, icon: "eye", note: `fonte principal: ${overview.metrics.pageviews_source === "vercel" ? "Vercel" : "tracker Nexo"}` },
    { label: overview.metrics.visitors_source === "vercel" ? "Visitantes por dia" : "Sessões Nexo", value: numberFormat.format(overview.metrics.visitors), change: overview.comparison.visitors_percent, icon: "activity", note: overview.metrics.visitors_source === "vercel" ? "soma diária informada pela Vercel" : "identificador temporário por aba" },
    { label: "Visualizações / visitante ou sessão", value: decimalFormat.format(overview.metrics.pageviews_per_visitor), change: null, icon: "layers", note: "média na fonte principal" },
    { label: "Sessões com interação", value: `${decimalFormat.format(overview.metrics.engagement_percent)}%`, change: null, icon: "sparkle", note: `${numberFormat.format(overview.metrics.engaged_sessions)} sessões com evento Nexo` },
    { label: "Tempo médio na página", value: formatDuration(overview.time_metrics.average_page_seconds), change: null, icon: "clock", note: `${numberFormat.format(overview.time_metrics.page_samples)} tempos medidos pelo Nexo` },
    { label: "Tempo médio da sessão", value: formatDuration(overview.time_metrics.average_session_seconds), change: null, icon: "clock", note: `${numberFormat.format(overview.time_metrics.measured_sessions)} sessões medidas pelo Nexo` },
    { label: "Taxa de uma página", value: `${decimalFormat.format(overview.metrics.bounce_rate_percent)}%`, change: null, icon: "activity", note: "sessões Nexo com um único pageview" },
    { label: "Combinações técnicas", value: numberFormat.format(overview.metrics.device_profile_count), change: null, icon: "layers", note: "tipo + navegador + sistema; não identifica aparelhos" },
  ] : [];
  const combinedEvents = overview ? [...overview.events, ...overview.vercel_events].sort((a, b) => b.count - a.count) : [];
  const portfolioUrl = `https://${overview?.domain ?? "luca-toniolo.vercel.app"}`;

  const today = new Intl.DateTimeFormat("pt-BR", { weekday: "long", day: "2-digit", month: "long", year: "numeric" }).format(new Date());

  return (
    <div className="dashboard-layout">
      {mobileMenuOpen && (
        <button className="sidebar-scrim" type="button" aria-label="Fechar menu" onClick={() => setMobileMenuOpen(false)} />
      )}

      <aside className={`sidebar${mobileMenuOpen ? " sidebar-open" : ""}`}>
        <div className="sidebar-brand-row">
          <Brand light />
          <button className="sidebar-close" type="button" onClick={() => setMobileMenuOpen(false)} aria-label="Fechar menu"><Icon name="close" size={19} /></button>
        </div>
        <div className="workspace-switcher">
          <span className="workspace-avatar">LT</span>
          <span className="workspace-copy"><small>ESPAÇO DE TRABALHO</small><strong>Luca Toniolo</strong></span>
          <Icon name="chevron-down" size={16} />
        </div>
        <nav className="sidebar-nav" aria-label="Navegação principal">
          <span className="nav-caption">WORKSPACE</span>
          <Link className="sidebar-link active" to="/dashboard" onClick={() => setMobileMenuOpen(false)}><Icon name="grid" size={18} /> Visão geral</Link>
          <span className="sidebar-link future-link" aria-disabled="true"><Icon name="globe" size={18} /> Sites <small>EM BREVE</small></span>
          <span className="nav-caption nav-caption-spaced">ANÁLISE</span>
          <span className="sidebar-link future-link" aria-disabled="true"><Icon name="chart" size={18} /> Relatórios</span>
          <span className="sidebar-link future-link" aria-disabled="true"><Icon name="activity" size={18} /> Eventos</span>
          <span className="nav-caption nav-caption-spaced">PREFERÊNCIAS</span>
          <span className="sidebar-link future-link" aria-disabled="true"><Icon name="shield" size={18} /> Privacidade</span>
        </nav>
        <div className="sidebar-site-card">
          <div className="site-card-heading"><span className="site-mini-mark">LT</span><span>PORTFÓLIO CONECTADO</span></div>
          <strong>{overview?.domain ?? "luca-toniolo.vercel.app"}</strong>
          <span className={`site-pending${overview?.sources.nexo === "receiving" || overview?.sources.vercel === "connected" ? " site-connected" : ""}`}><i /> {overview?.sources.vercel === "connected" ? "Vercel + Nexo ativos" : overview?.sources.nexo === "receiving" ? "Tracker Nexo recebendo dados" : "Aguardando dados do portfólio"}</span>
          <a href={portfolioUrl} target="_blank" rel="noreferrer">Abrir portfólio <Icon name="external" size={13} /></a>
        </div>
        <div className="sidebar-profile">
          <span className="profile-avatar">LT</span>
          <span className="profile-copy"><strong>Luca Toniolo</strong><small>Administrador</small></span>
          <button className="logout-button" type="button" onClick={leaveDashboard} aria-label="Sair da conta" title="Sair"><Icon name="logout" size={17} /></button>
        </div>
      </aside>

      <div className="dashboard-main">
        <header className="dashboard-topbar">
          <button className="mobile-menu-button" type="button" onClick={() => setMobileMenuOpen(true)} aria-label="Abrir menu"><Icon name="menu" size={20} /></button>
          <div className="topbar-breadcrumb"><span>Workspace</span><span>/</span><strong>Visão geral</strong></div>
          <a className="topbar-portfolio-link" href={portfolioUrl} target="_blank" rel="noreferrer">Ver portfólio <Icon name="arrow-up-right" size={15} /></a>
        </header>

        <main className="dashboard-content">
          <div className="dashboard-heading-row">
            <div>
              <p className="dashboard-overline">{today.toLocaleUpperCase("pt-BR")}</p>
              <h1>Visão geral</h1>
              <p className="dashboard-subtitle">Métricas da Vercel combinadas com eventos coletados diretamente pelo Nexo.</p>
            </div>
            <label className="period-pill"><Icon name="calendar" size={16} /><span className="sr-only">Período de análise</span>
              <select className="period-select" value={days} onChange={(event) => setDays(Number(event.target.value))}>
                <option value={7}>Últimos 7 dias</option>
                <option value={30}>Últimos 30 dias</option>
                <option value={90}>Últimos 90 dias</option>
              </select>
              <Icon name="chevron-down" size={15} />
            </label>
          </div>

          {loading && <div className="dashboard-state" role="status"><span className="loading-indicator" /> Consultando as fontes de dados do portfólio…</div>}
          {errorMessage && <div className="dashboard-state dashboard-error" role="alert"><Icon name="info" size={18} /><span><strong>Não foi possível carregar os dados</strong><small>{errorMessage}</small></span><button type="button" onClick={() => setRefreshKey((current) => current + 1)}>Tentar novamente</button></div>}

          {overview && !loading && <>
            <div className="data-source-banner" role="note">
              <span className="data-source-icon"><Icon name="shield" size={17} /></span>
              <p><strong>{overview.sources.vercel === "connected" ? "Vercel Web Analytics + tracker próprio Nexo" : overview.sources.vercel === "unavailable" ? "Usando o tracker próprio Nexo" : "Tracker próprio Nexo"}</strong><span>{overview.sources.vercel === "connected" ? `Vercel: ${numberFormat.format(overview.metrics.vercel_pageviews ?? 0)} pageviews; Nexo: ${numberFormat.format(overview.metrics.nexo_pageviews)}. O painel usa a Vercel como fonte principal sem somar as contagens. Sessões e interações vêm do Nexo.` : "As métricas vêm dos eventos que o portfólio envia ao Nexo. Ao instalar/configurar a Vercel, ela será a fonte principal de pageviews e o tracker continuará complementando as interações."}</span></p>
              <span className="data-source-tag"><i /> {overview.sources.nexo === "receiving" ? "NEXO RECEBENDO" : overview.sources.vercel === "connected" ? "VERCEL CONECTADA" : "AGUARDANDO TRACKER"}</span>
            </div>

            <section className="metric-grid" aria-label="Métricas resumidas">
              {metrics.map((metric) => (
                <article className="metric-card" key={metric.label}>
                  <div className="metric-card-top"><span>{metric.label}</span><span className="metric-icon"><Icon name={metric.icon} size={17} /></span></div>
                  <strong className="metric-value">{metric.value}</strong>
                  <div className="metric-footer"><span className={`metric-change${metric.change !== null && metric.change < 0 ? " metric-change-down" : ""}`}>{formatChange(metric.change)}</span><span>{metric.note}</span></div>
                </article>
              ))}
            </section>

            <section className="analytics-grid" aria-label="Detalhes da atividade">
              <article className="panel chart-panel">
                <div className="panel-heading">
                  <div><span className="panel-overline">TRÁFEGO DO SITE</span><h2>Visualizações ao longo do tempo</h2><p>{formatDate(overview.period_start)} a {formatDate(overview.period_end)}</p></div>
                  <span className="chart-total"><strong>{numberFormat.format(overview.metrics.pageviews)}</strong><small>visualizações</small></span>
                </div>
                <div className="main-chart">
                  <div className="chart-axis-labels">{chartTicks.map((tick, index) => <span key={`${tick}-${index}`}>{numberFormat.format(tick)}</span>)}</div>
                  <div className="chart-plot">
                    <div className="chart-grid-lines"><i /><i /><i /><i /><i /></div>
                    <svg viewBox="0 0 800 236" preserveAspectRatio="none" role="img" aria-label={`Gráfico de visualizações nos últimos ${days} dias`}>
                      <defs><linearGradient id="trafficFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#9cc96d" stopOpacity=".3" /><stop offset="100%" stopColor="#9cc96d" stopOpacity="0" /></linearGradient></defs>
                      {chart.area && <path d={chart.area} fill="url(#trafficFill)" />}
                      {chart.line && <path d={chart.line} fill="none" stroke="#628e50" strokeWidth="2.5" vectorEffect="non-scaling-stroke" />}
                    </svg>
                  </div>
                </div>
                <div className="chart-x-labels">{dateTicks.map((day) => <span key={day.date}>{formatDate(day.date, { day: "2-digit", month: "short" })}</span>)}</div>
                <div className="chart-legend"><i /><span>Visualizações · {overview.metrics.pageviews_source === "vercel" ? "Vercel" : "Nexo"}</span><small>{formatChange(overview.comparison.pageviews_percent)} vs. período anterior</small></div>
              </article>

              <article className="panel events-panel">
                <div className="panel-heading compact-heading"><div><span className="panel-overline">INTERAÇÕES</span><h2>Eventos personalizados</h2></div><span className="small-count">{days} DIAS</span></div>
                {combinedEvents.length > 0 ? <div className="event-list">
                  {combinedEvents.slice(0, 6).map((event) => (
                    <div className="event-row" key={`${event.source}:${event.name}`}>
                      <span className="event-icon"><Icon name="sparkle" size={16} /></span>
                      <span className="event-copy"><strong>{event.name}</strong><small>{event.source === "nexo" ? `${numberFormat.format(event.sessions)} sessões · Nexo` : `${numberFormat.format(event.visitors)} visitantes agregados · Vercel`}</small></span>
                      <span className="event-count">{numberFormat.format(event.count)}</span>
                    </div>
                  ))}
                </div> : <div className="empty-events"><Icon name="activity" size={20} /><strong>Nenhuma interação recebida</strong><span>Instale o tracker Nexo no portfólio e chame track() nos links de currículo, projetos e contato. Eventos Vercel aparecem separadamente quando disponíveis.</span></div>}
                <div className="event-footnote"><Icon name="lock" size={14} /> Eventos Vercel e Nexo aparecem separados; cada contagem mantém sua origem.</div>
              </article>
            </section>

            <section className="demographics-grid" aria-label="Dispositivos e localização estimada">
              <BreakdownPanel title="Dispositivos" kind="device" items={overview.devices} emptyMessage="Aguardando dados de dispositivo." />
              <BreakdownPanel title="Navegadores" kind="browser" items={overview.browsers} emptyMessage="Aguardando dados de navegador." />
              <BreakdownPanel title="Sistemas operacionais" kind="os" items={overview.operating_systems} emptyMessage="Aguardando dados de sistema." />
              <BreakdownPanel title="Regiões estimadas" kind="region" items={overview.regions} emptyMessage="Localização indisponível nesta fonte." />
            </section>

            <section className="time-summary-grid" aria-label="Tempos de navegação">
              <article className="panel time-summary-panel">
                <div className="panel-heading compact-heading"><div><span className="panel-overline">TEMPO ATIVO · NEXO</span><h2>Tempo nas páginas</h2></div><Icon name="clock" size={18} /></div>
                <div className="time-stats">
                  <div><span>Média</span><strong>{formatDuration(overview.time_metrics.average_page_seconds)}</strong></div>
                  <div><span>Mínimo</span><strong>{formatDuration(overview.time_metrics.minimum_page_seconds)}</strong></div>
                  <div><span>Máximo</span><strong>{formatDuration(overview.time_metrics.maximum_page_seconds)}</strong></div>
                  <div><span>Amostras</span><strong>{numberFormat.format(overview.time_metrics.page_samples)}</strong></div>
                </div>
                <p className="time-summary-note">Conta o tempo em que a página ficou visível na aba. Tempo em segundo plano é pausado.</p>
              </article>
              <article className="panel time-summary-panel">
                <div className="panel-heading compact-heading"><div><span className="panel-overline">SESSÕES · NEXO</span><h2>Duração das sessões</h2></div><Icon name="activity" size={18} /></div>
                <div className="time-stats">
                  <div><span>Média</span><strong>{formatDuration(overview.time_metrics.average_session_seconds)}</strong></div>
                  <div><span>Mínimo</span><strong>{formatDuration(overview.time_metrics.minimum_session_seconds)}</strong></div>
                  <div><span>Máximo</span><strong>{formatDuration(overview.time_metrics.maximum_session_seconds)}</strong></div>
                  <div><span>Amostras</span><strong>{numberFormat.format(overview.time_metrics.measured_sessions)}</strong></div>
                </div>
                <p className="time-summary-note">Uma sessão é uma aba do navegador; não equivale necessariamente a uma pessoa ou aparelho.</p>
              </article>
            </section>

            <section className="bottom-grid">
              <article className="panel pages-panel">
                <div className="panel-heading compact-heading"><div><span className="panel-overline">CONTEÚDO</span><h2>Páginas populares</h2></div><span className="small-count">{days} DIAS</span></div>
                {overview.popular_pages.length > 0 ? <div className="pages-table" role="table" aria-label="Páginas populares">
                  <div className="pages-table-head" role="row"><span role="columnheader">PÁGINA</span><span role="columnheader">VIEWS</span><span role="columnheader">TEMPO MÉDIO</span><span role="columnheader">DO TOTAL</span></div>
                  {overview.popular_pages.map((page) => (
                    <div className="pages-table-row" role="row" key={page.path}>
                      <span className="page-cell" role="cell"><strong>{pageTitle(page.path)}</strong><small>{page.path}</small></span>
                      <span role="cell">{numberFormat.format(page.pageviews)}</span>
                      <span className="page-duration-cell" role="cell"><strong>{formatDuration(page.average_time_seconds)}</strong><small>{formatDuration(page.minimum_time_seconds)} – {formatDuration(page.maximum_time_seconds)}</small></span>
                      <span className="share-cell" role="cell">{decimalFormat.format(page.share_percent)}%</span>
                    </div>
                  ))}
                </div> : <p className="empty-copy">Ainda não há páginas no período selecionado.</p>}
              </article>

              <article className="panel connection-panel">
                <div className="panel-heading compact-heading"><div><span className="panel-overline">ANÁLISE AUTOMÁTICA</span><h2>O que os dados mostram</h2></div><span className="connection-icon"><Icon name="chart" size={18} /></span></div>
                <ul className="insight-list">{overview.insights.map((insight) => <li key={insight}><Icon name="sparkle" size={15} /><span>{insight}</span></li>)}</ul>
                <div className="connection-domain"><span className="domain-favicon">LT</span><span><strong>{overview.domain}</strong><small>{overview.sources.vercel === "connected" ? "Vercel Web Analytics" : "Portfólio configurado para o Nexo"}</small></span><span className={`connection-status${overview.sources.vercel === "connected" || overview.sources.nexo === "receiving" ? " connection-status-active" : ""}`}><i /> {overview.sources.vercel === "connected" ? "Vercel ativa" : overview.sources.nexo === "receiving" ? "Nexo ativo" : "Sem eventos"}</span></div>
                <a className="portfolio-button" href={portfolioUrl} target="_blank" rel="noreferrer">Abrir portfólio <Icon name="arrow-up-right" size={16} /></a>
                <div className="connection-footnote"><Icon name="info" size={14} /> Pageviews vêm de uma única fonte principal; o tracker Nexo mede sessões e interações próprias.</div>
              </article>
            </section>

            <footer className="dashboard-footer"><span>NEXO ANALYTICS <i /> VERCEL + COLETA PRÓPRIA</span><button type="button" onClick={leaveDashboard}>Sair da conta</button></footer>
          </>}
        </main>
      </div>
    </div>
  );
}
