import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Brand from "../components/Brand";
import Icon from "../components/Icon";
import { ApiError, login } from "../lib/api";

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setErrorMessage("");
    const form = new FormData(event.currentTarget);
    try {
      await login(String(form.get("email") || ""), String(form.get("password") || ""));
      navigate("/dashboard", { replace: true });
    } catch (error) {
      setErrorMessage(error instanceof ApiError ? error.message : "Não foi possível entrar. Tente novamente.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-layout">
      <section className="login-showcase" aria-label="Apresentação do Nexo Analytics">
        <div className="showcase-glow showcase-glow-one" />
        <div className="showcase-glow showcase-glow-two" />
        <Brand light />

        <div className="showcase-body">
          <p className="eyebrow"><span className="eyebrow-dot" /> ANALYTICS PARA TODOS OS SEUS SITES</p>
          <h1>Uma visão mais clara do que você <em>constrói.</em></h1>
          <p className="showcase-description">
            Acompanhe projetos, visitas e sinais de interesse em um só lugar —
            com métricas úteis e privacidade desde o início.
          </p>

          <div className="preview-card" aria-label="Prévia ilustrativa de métricas">
            <div className="preview-topline">
              <span className="preview-label">PRÉVIA ILUSTRATIVA <span>/</span> 30 DIAS</span>
              <span className="preview-status"><span /> EXEMPLO</span>
            </div>
            <div className="preview-metric-row">
              <div>
                <span className="preview-metric-label">VISUALIZAÇÕES DE PÁGINA</span>
                <strong>8.421</strong>
              </div>
              <span className="preview-change"><Icon name="arrow-up" size={13} /> 12,8%</span>
            </div>
            <div className="preview-chart">
              <div className="preview-chart-grid"><i /><i /><i /></div>
              <svg viewBox="0 0 560 116" preserveAspectRatio="none" aria-hidden="true">
                <defs>
                  <linearGradient id="previewFill" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor="#c9f17c" stopOpacity=".22" />
                    <stop offset="100%" stopColor="#c9f17c" stopOpacity="0" />
                  </linearGradient>
                </defs>
                <path d="M0 89 C30 82 36 92 61 76 S98 78 124 66 S156 70 183 56 S214 67 245 47 S282 57 307 42 S344 54 369 31 S410 42 434 25 S469 41 489 21 S526 33 545 9 S554 9 560 14 V116 H0Z" fill="url(#previewFill)" />
                <path d="M0 89 C30 82 36 92 61 76 S98 78 124 66 S156 70 183 56 S214 67 245 47 S282 57 307 42 S344 54 369 31 S410 42 434 25 S469 41 489 21 S526 33 545 9 S554 9 560 14" fill="none" stroke="#c9f17c" strokeWidth="2.4" vectorEffect="non-scaling-stroke" />
                <circle cx="545" cy="9" r="4" fill="#c9f17c" />
              </svg>
            </div>
            <div className="preview-dates"><span>18 set</span><span>25 set</span><span>02 out</span><span>09 out</span><span>17 out</span></div>
          </div>
        </div>

        <div className="showcase-footer">
          <span><Icon name="shield" size={16} /> Privacidade por padrão</span>
          <span>Construído para entender, não vigiar.</span>
        </div>
      </section>

      <section className="login-panel">
        <div className="login-mobile-brand"><Brand /></div>
        <div className="login-form-wrap">
          <div className="login-form-heading">
            <span className="form-overline">SUA ÁREA DE TRABALHO</span>
            <h2>Boas-vindas de volta.</h2>
            <p>Entre na sua conta para continuar.</p>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <label className="field-label" htmlFor="email">E-mail</label>
            <div className="input-wrap">
              <Icon name="mail" size={18} />
              <input
                id="email"
                name="email"
                type="email"
                placeholder="voce@exemplo.com"
                autoComplete="email"
                required
              />
            </div>

            <div className="password-heading">
              <label className="field-label" htmlFor="password">Senha</label>
              <span className="form-note">Sessão segura</span>
            </div>
            <div className="input-wrap">
              <Icon name="lock" size={18} />
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="Sua senha"
                autoComplete="current-password"
                required
              />
              <button
                className="input-action"
                type="button"
                onClick={() => setShowPassword((visible) => !visible)}
                aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
              >
                <Icon name={showPassword ? "eye-off" : "eye"} size={18} />
              </button>
            </div>

            {errorMessage && <p className="form-error" role="alert">{errorMessage}</p>}

            <button className="button-primary login-submit" type="submit" disabled={loading}>
              {loading ? "Verificando acesso..." : "Entrar no painel"} {!loading && <Icon name="arrow-up-right" size={18} />}
            </button>
          </form>

          <p className="demo-note"><Icon name="info" size={16} />
            Entre com o e-mail e a senha do administrador configurados no backend.
          </p>

          <div className="login-bottom-links">
            <span>Quer conhecer o projeto?</span>
            <a href="https://luca-toniolo.vercel.app" target="_blank" rel="noreferrer">
              Visitar portfólio <Icon name="external" size={14} />
            </a>
          </div>
        </div>
        <p className="login-copyright">© 2026 Nexo Analytics <span>·</span> Feito para dar clareza aos seus dados.</p>
      </section>
    </main>
  );
}
