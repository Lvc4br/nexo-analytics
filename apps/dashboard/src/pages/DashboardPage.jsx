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
    { label: "Visualizações de página", value: numberFormat.format(overview.metrics.pageviews), change: overview.comparison.pageviews_percent, icon: "eye", note: "vs. período anterior" },
    { label: "Visitantes por dia", value: numberFormat.format(overview.metrics.visitors), change: overview.comparison.visitors_percent, icon: "activity", note: "soma diária do período" },
    { label: "Visualizações / visitante-dia", value: decimalFormat.format(overview.metrics.pageviews_per_visitor), change: null, icon: "layers", note: "média no período" },
    { label: "Eventos personalizados", value: numberFormat.format(overview.metrics.events), change: overview.comparison.events_percent, icon: "sparkle", note: "enviados pelo portfólio" },
  ] : [];

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
          <span className={`site-pending${overview ? " site-connected" : ""}`}><i /> {overview ? "Sincronizado com a Vercel" : "Conectando à Vercel"}</span>
          <a href="https://luca-toniolo.vercel.app" target="_blank" rel="noreferrer">Abrir portfólio <Icon name="external" size={13} /></a>
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
          <a className="topbar-portfolio-link" href="https://luca-toniolo.vercel.app" target="_blank" rel="noreferrer">Ver portfólio <Icon name="arrow-up-right" size={15} /></a>
        </header>

        <main className="dashboard-content">
          <div className="dashboard-heading-row">
            <div>
              <p className="dashboard-overline">{today.toLocaleUpperCase("pt-BR")}</p>
              <h1>Visão geral</h1>
              <p className="dashboard-subtitle">Dados do portfólio consultados na Vercel.</p>
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

          {loading && <div className="dashboard-state" role="status"><span className="loading-indicator" /> Consultando o Web Analytics da Vercel…</div>}
          {errorMessage && <div className="dashboard-state dashboard-error" role="alert"><Icon name="info" size={18} /><span><strong>Não foi possível carregar os dados</strong><small>{errorMessage}</small></span><button type="button" onClick={() => setRefreshKey((current) => current + 1)}>Tentar novamente</button></div>}

          {overview && !loading && <>
            <div className="data-source-banner" role="note">
              <span className="data-source-icon"><Icon name="shield" size={17} /></span>
              <p><strong>Fonte conectada: Vercel Web Analytics</strong><span>Comparação com os {days} dias anteriores. Visitantes são somados por dia, como a Vercel define esse indicador.</span></p>
              <span className="data-source-tag"><i /> DADOS REAIS</span>
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
                <div className="chart-legend"><i /><span>Visualizações de página</span><small>{formatChange(overview.comparison.pageviews_percent)} vs. período anterior</small></div>
              </article>

              <article className="panel events-panel">
                <div className="panel-heading compact-heading"><div><span className="panel-overline">INTERAÇÕES</span><h2>Eventos personalizados</h2></div><span className="small-count">{days} DIAS</span></div>
                {overview.events.length > 0 ? <div className="event-list">
                  {overview.events.slice(0, 6).map((event) => (
                    <div className="event-row" key={event.name}>
                      <span className="event-icon"><Icon name="sparkle" size={16} /></span>
                      <span className="event-copy"><strong>{event.name}</strong><small>{numberFormat.format(event.visitors)} visitantes</small></span>
                      <span className="event-count">{numberFormat.format(event.count)}</span>
                    </div>
                  ))}
                </div> : <div className="empty-events"><Icon name="activity" size={20} /><strong>Nenhum evento personalizado</strong><span>As visualizações de página continuam sendo coletadas automaticamente. Eventos de interação dependem da instrumentação no portfólio e do plano da Vercel.</span></div>}
                <div className="event-footnote"><Icon name="lock" size={14} /> Exibimos apenas dados agregados retornados pela Vercel.</div>
              </article>
            </section>

            <section className="bottom-grid">
              <article className="panel pages-panel">
                <div className="panel-heading compact-heading"><div><span className="panel-overline">CONTEÚDO</span><h2>Páginas populares</h2></div><span className="small-count">{days} DIAS</span></div>
                {overview.popular_pages.length > 0 ? <div className="pages-table" role="table" aria-label="Páginas populares">
                  <div className="pages-table-head" role="row"><span role="columnheader">PÁGINA</span><span role="columnheader">VISUALIZAÇÕES</span><span role="columnheader">DO TOTAL</span></div>
                  {overview.popular_pages.map((page) => (
                    <div className="pages-table-row" role="row" key={page.path}>
                      <span className="page-cell" role="cell"><strong>{pageTitle(page.path)}</strong><small>{page.path}</small></span>
                      <span role="cell">{numberFormat.format(page.pageviews)}</span>
                      <span className="share-cell" role="cell">{decimalFormat.format(page.share_percent)}%</span>
                    </div>
                  ))}
                </div> : <p className="empty-copy">Ainda não há páginas no período selecionado.</p>}
              </article>

              <article className="panel connection-panel">
                <div className="panel-heading compact-heading"><div><span className="panel-overline">ANÁLISE AUTOMÁTICA</span><h2>O que os dados mostram</h2></div><span className="connection-icon"><Icon name="chart" size={18} /></span></div>
                <ul className="insight-list">{overview.insights.map((insight) => <li key={insight}><Icon name="sparkle" size={15} /><span>{insight}</span></li>)}</ul>
                <div className="connection-domain"><span className="domain-favicon">LT</span><span><strong>{overview.domain}</strong><small>Web Analytics da Vercel</small></span><span className="connection-status connection-status-active"><i /> Conectado</span></div>
                <a className="portfolio-button" href="https://luca-toniolo.vercel.app" target="_blank" rel="noreferrer">Abrir portfólio <Icon name="arrow-up-right" size={16} /></a>
                <div className="connection-footnote"><Icon name="info" size={14} /> Comparações e visitantes seguem a agregação diária da Vercel.</div>
              </article>
            </section>

            <footer className="dashboard-footer"><span>NEXO ANALYTICS <i /> DADOS CONSULTADOS NA VERCEL</span><button type="button" onClick={leaveDashboard}>Sair da conta</button></footer>
          </>}
        </main>
      </div>
    </div>
  );
}
