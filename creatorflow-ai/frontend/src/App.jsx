import { useState } from "react";

import { generateContent } from "./api";

const INITIAL_FORM = {
  topic: "Docker vs Kubernetes",
  audience: "Beginners",
  language: "English",
  tone: "Simple",
  duration: "8 minutes",
  goal: "Educational video",
};

const SECTIONS = [
  { key: "topic_analysis", title: "Topic Analysis", eyebrow: "Strategy", icon: "◎" },
  { key: "titles", title: "Title Ideas", eyebrow: "Discovery", icon: "Aa" },
  { key: "script", title: "Video Script", eyebrow: "Long-form", icon: "¶" },
  {
    key: "thumbnail_texts",
    title: "Thumbnail Text",
    eyebrow: "Visual hook",
    icon: "◇",
  },
  { key: "seo", title: "SEO Package", eyebrow: "Reach", icon: "#" },
  { key: "shorts", title: "Shorts & Reels", eyebrow: "Repurpose", icon: "▶" },
  { key: "review", title: "Quality Review", eyebrow: "Quality gate", icon: "✓" },
];

const QUICK_TOPICS = [
  "Docker vs Kubernetes",
  "How AI agents work",
  "Learn Python in 2026",
];

const AGENTS = ["Topic", "Titles", "Script", "Thumbnail", "SEO", "Shorts", "Review"];

function humanize(value) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function ValueView({ value, name = "" }) {
  if (Array.isArray(value)) {
    const primitives = value.every(
      (item) => typeof item === "string" || typeof item === "number",
    );

    if (primitives && ["tags", "hashtags", "thumbnail_texts"].includes(name)) {
      return (
        <div className={name === "thumbnail_texts" ? "thumbnail-grid" : "chips"}>
          {value.map((item) => (
            <span className={name === "thumbnail_texts" ? "thumbnail-tile" : "chip"} key={item}>
              {item}
            </span>
          ))}
        </div>
      );
    }

    return (
      <ol className={primitives ? `content-list ${name}-list` : "nested-list"}>
        {value.map((item, index) => (
          <li key={`${name}-${index}`}>
            <ValueView value={item} />
          </li>
        ))}
      </ol>
    );
  }

  if (value && typeof value === "object") {
    return (
      <div className="property-group">
        {Object.entries(value).map(([key, nestedValue]) => (
          <div className="property" key={key}>
            <h3>{humanize(key)}</h3>
            <ValueView value={nestedValue} name={key} />
          </div>
        ))}
      </div>
    );
  }

  if (name === "quality_score") {
    return (
      <div className="score">
        <strong>{value}</strong>
        <span>/ 10</span>
      </div>
    );
  }

  return <p className="copy">{String(value)}</p>;
}

function ResultCard({ section, value }) {
  return (
    <article className={`result-card result-${section.key}`}>
      <header className="card-header">
        <div className="card-title">
          <span className="section-icon" aria-hidden="true">
            {section.icon}
          </span>
          <div>
            <span className="eyebrow">{section.eyebrow}</span>
            <h2>{section.title}</h2>
          </div>
        </div>
        <span className="complete-pill">
          <span className="complete-dot" />
          Complete
        </span>
      </header>
      <ValueView value={value} name={section.key} />
    </article>
  );
}

function App() {
  const [form, setForm] = useState(INITIAL_FORM);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (!form.topic.trim()) {
      setError("Please enter a YouTube topic.");
      return;
    }

    setLoading(true);

    try {
      const contentPackage = await generateContent(form);
      setResult(contentPackage);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <nav className="topbar">
          <div className="brand">
            <span className="brand-mark">
              <span>CF</span>
            </span>
            <span className="brand-name">CreatorFlow <b>AI</b></span>
          </div>
          <div className="topbar-status">
            <span className="live-dot" />
            Demo mode · No API key
          </div>
        </nav>

        <div className="hero-layout">
          <div className="hero-copy">
            <span className="kicker">
              <span>✦</span>
              Ruflo-inspired content orchestration
            </span>
            <h1>
              Turn one idea into a <em>complete</em> content system.
            </h1>
            <p>
              A coordinated studio of specialist agents creates your strategy,
              script, SEO, thumbnails, Shorts, and quality review in one flow.
            </p>
            <div className="hero-metrics">
              <span><strong>8</strong> focused agents</span>
              <span><strong>1</strong> polished package</span>
              <span><strong>0</strong> prompt juggling</span>
            </div>
          </div>

          <div className="hero-visual" aria-hidden="true">
            <div className="visual-glow" />
            <div className="flow-preview">
              <div className="preview-top">
                <span>Creator workflow</span>
                <span className="preview-live"><i /> Live</span>
              </div>
              <div className="preview-topic">
                <span className="preview-play">▶</span>
                <div>
                  <small>Current brief</small>
                  <strong>{form.topic || "Your next video idea"}</strong>
                </div>
              </div>
              <div className="preview-agents">
                {AGENTS.slice(0, 4).map((agent, index) => (
                  <div className="preview-agent" key={agent}>
                    <span>{index + 1}</span>
                    <div>
                      <strong>{agent} Agent</strong>
                      <small>{index === 3 ? "Waiting in queue" : "Ready to run"}</small>
                    </div>
                    <i className={index === 3 ? "waiting" : ""}>✓</i>
                  </div>
                ))}
              </div>
              <div className="preview-footer">
                <span><b>7</b> deliverables</span>
                <span><b>8.7</b> quality score</span>
              </div>
            </div>
            <div className="floating-note note-one">SEO ready <b>#</b></div>
            <div className="floating-note note-two"><b>▶</b> 2 Shorts</div>
          </div>
        </div>

        <div className="agent-strip" aria-label="Agent workflow">
          {AGENTS.map((agent, index) => (
            <span key={agent}>
              <b>{String(index + 1).padStart(2, "0")}</b>
              <i />
              {agent}
            </span>
          ))}
        </div>
      </section>

      <div className="workspace">
        <aside className="control-panel">
          <div className="panel-heading">
            <div className="panel-number">01</div>
            <div>
              <span className="eyebrow">Creative brief</span>
              <h2>Shape your video</h2>
              <p>Set the direction. Your agents handle the rest.</p>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <label>
              <span className="field-label">
                Topic <b>Required</b>
              </span>
              <textarea
                name="topic"
                value={form.topic}
                onChange={updateField}
                placeholder="e.g. Docker vs Kubernetes"
                rows="3"
                required
              />
            </label>

            <div className="quick-topics">
              {QUICK_TOPICS.map((topic) => (
                <button
                  type="button"
                  key={topic}
                  onClick={() => setForm((current) => ({ ...current, topic }))}
                >
                  {topic}
                </button>
              ))}
            </div>

            <div className="field-grid">
              <label>
                <span className="field-label">Audience</span>
                <input
                  name="audience"
                  value={form.audience}
                  onChange={updateField}
                />
              </label>
              <label>
                <span className="field-label">Language</span>
                <select name="language" value={form.language} onChange={updateField}>
                  <option>English</option>
                  <option>Hindi</option>
                  <option>Spanish</option>
                  <option>French</option>
                  <option>German</option>
                </select>
              </label>
              <label>
                <span className="field-label">Tone</span>
                <select name="tone" value={form.tone} onChange={updateField}>
                  <option>Simple</option>
                  <option>Professional</option>
                  <option>Conversational</option>
                  <option>Energetic</option>
                  <option>Story-driven</option>
                </select>
              </label>
              <label>
                <span className="field-label">Duration</span>
                <input
                  name="duration"
                  value={form.duration}
                  onChange={updateField}
                />
              </label>
            </div>

            <label>
              <span className="field-label">Content goal</span>
              <input name="goal" value={form.goal} onChange={updateField} />
            </label>

            <button className="generate-button" type="submit" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner" />
                  Agents are working…
                </>
              ) : (
                <>
                  <span>
                    <b>✦</b>
                    Generate content package
                  </span>
                  <i aria-hidden="true">→</i>
                </>
              )}
            </button>

            <p className="form-note">
              <span>⌁</span> Powered by a sequential 8-agent workflow
            </p>

            {error && (
              <div className="error-message" role="alert">
                <strong>Generation stopped</strong>
                <span>{error}</span>
              </div>
            )}
          </form>
        </aside>

        <section className="results" aria-live="polite">
          {!result && !loading && (
            <div className="empty-state">
              <div className="empty-orbit">
                <span>✦</span>
                {AGENTS.slice(0, 4).map((agent) => (
                  <i key={agent} />
                ))}
              </div>
              <span className="eyebrow">Ready when you are</span>
              <h2>Your creative team is standing by.</h2>
              <p>
                Submit your brief and seven specialist agents will build the
                package, followed by one final response agent.
              </p>
              <div className="empty-deliverables">
                <span>Strategy</span>
                <span>Script</span>
                <span>SEO</span>
                <span>Shorts</span>
              </div>
            </div>
          )}

          {loading && (
            <div className="loading-state">
              <div className="loading-track">
                <span />
              </div>
              <span className="eyebrow">Orchestrating agents</span>
              <h2>Building your content package…</h2>
              <p>Strategy first, quality review last. The good kind of assembly line.</p>
            </div>
          )}

          {result && !loading && (
            <>
              <div className="results-heading">
                <div>
                  <span className="eyebrow">✦ Generation complete</span>
                  <h2>{result.request.topic}</h2>
                  <p>Your publish-ready content workspace</p>
                </div>
                <span className="workflow-badge">
                  <i>✓</i>
                  {result.workflow.agents_executed.length} agents complete
                </span>
              </div>

              {SECTIONS.map((section) => (
                <ResultCard
                  key={section.key}
                  section={section}
                  value={result[section.key]}
                />
              ))}
            </>
          )}
        </section>
      </div>
    </main>
  );
}

export default App;
