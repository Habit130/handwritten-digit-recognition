import { useEffect, useMemo, useState } from "react";

import { CodePane } from "./components/CodePane";
import { DrawingCanvas } from "./components/DrawingCanvas";
import { NetworkStage } from "./components/NetworkStage";
import { api, LabApiError } from "./lib/api";
import type {
  ChallengeRoute,
  CodeFile,
  ModelStatus,
  NetworkContract,
  NetworkTrace,
  RouteId,
  Workspace,
} from "./lib/types";

const SPEEDS = [
  { label: "0.5×", milliseconds: 2200 },
  { label: "1×", milliseconds: 1300 },
  { label: "1.5×", milliseconds: 800 },
] as const;

function errorText(error: unknown): string {
  if (error instanceof LabApiError) {
    return `${error.message}｜${error.stage}: ${error.detail}`;
  }
  return error instanceof Error ? error.message : String(error);
}

function PlaybackControls({
  selectedIndex,
  layerCount,
  playing,
  speedIndex,
  onPlayingChange,
  onSelectedIndexChange,
  onSpeedChange,
}: {
  selectedIndex: number;
  layerCount: number;
  playing: boolean;
  speedIndex: number;
  onPlayingChange: (playing: boolean) => void;
  onSelectedIndexChange: (index: number) => void;
  onSpeedChange: (index: number) => void;
}) {
  return (
    <div className="playback-controls" aria-label="动态叙事控制">
      <button
        type="button"
        aria-label="回到第一层"
        onClick={() => {
          onSelectedIndexChange(0);
          onPlayingChange(false);
        }}
      >
        ↺
      </button>
      <button
        type="button"
        aria-label="上一层"
        disabled={selectedIndex === 0}
        onClick={() =>
          onSelectedIndexChange(Math.max(0, selectedIndex - 1))
        }
      >
        ←
      </button>
      <button
        className="play-button"
        type="button"
        onClick={() => onPlayingChange(!playing)}
      >
        {playing ? "暂停" : "播放"}
      </button>
      <button
        type="button"
        aria-label="下一层"
        disabled={selectedIndex === layerCount - 1}
        onClick={() =>
          onSelectedIndexChange(
            Math.min(layerCount - 1, selectedIndex + 1),
          )
        }
      >
        →
      </button>
      <div className="speed-control">
        {SPEEDS.map((speed, index) => (
          <button
            type="button"
            className={speedIndex === index ? "is-active" : ""}
            key={speed.label}
            onClick={() => onSpeedChange(index)}
          >
            {speed.label}
          </button>
        ))}
      </div>
      <span className="layer-counter">
        {String(selectedIndex + 1).padStart(2, "0")} /{" "}
        {String(layerCount).padStart(2, "0")}
      </span>
    </div>
  );
}

function EmptyScreen({ message }: { message: string }) {
  return (
    <main className="system-screen">
      <div className="system-mark">DIGIT // LAB</div>
      <div className="system-pulse" />
      <p>{message}</p>
    </main>
  );
}

export function App() {
  const [workspace, setWorkspace] = useState<Workspace>("walkthrough");
  const [contract, setContract] = useState<NetworkContract | null>(null);
  const [referenceTrace, setReferenceTrace] =
    useState<NetworkTrace | null>(null);
  const [liveTrace, setLiveTrace] = useState<NetworkTrace | null>(null);
  const [routes, setRoutes] = useState<ChallengeRoute[]>([]);
  const [routeId, setRouteId] = useState<RouteId>("direct");
  const [codeFiles, setCodeFiles] = useState<CodeFile[]>([]);
  const [selectedCodePath, setSelectedCodePath] = useState<string | null>(null);
  const [modelStatus, setModelStatus] = useState<ModelStatus>({
    loaded: false,
    route: null,
    model_path: null,
  });
  const [selectedLayer, setSelectedLayer] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [speedIndex, setSpeedIndex] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([
      api.contract(),
      api.referenceTrace(),
      api.routes(),
      api.modelStatus(),
    ])
      .then(([nextContract, nextTrace, nextRoutes, nextModelStatus]) => {
        if (
          nextContract.architecture_version !==
          nextTrace.architecture_version
        ) {
          throw new Error("网络契约与参考轨迹的架构版本不一致。");
        }
        setContract(nextContract);
        setReferenceTrace(nextTrace);
        setRoutes(nextRoutes);
        setModelStatus(nextModelStatus);
      })
      .catch((caught: unknown) => setError(errorText(caught)));
  }, []);

  useEffect(() => {
    void api
      .code(routeId)
      .then((response) => {
        setCodeFiles(response.files);
        setSelectedCodePath(response.files[0]?.path ?? null);
      })
      .catch((caught: unknown) => setError(errorText(caught)));
  }, [routeId]);

  useEffect(() => {
    if (!playing || contract === null) return;
    const timer = window.setInterval(() => {
      setSelectedLayer((current) => {
        if (current >= contract.layers.length - 1) {
          setPlaying(false);
          return current;
        }
        return current + 1;
      });
    }, SPEEDS[speedIndex]?.milliseconds ?? 1300);
    return () => window.clearInterval(timer);
  }, [contract, playing, speedIndex]);

  const route = useMemo(
    () => routes.find((item) => item.id === routeId) ?? null,
    [routeId, routes],
  );

  const shownTrace = workspace === "live" ? liveTrace : referenceTrace;
  const activeLayer = contract?.layers[selectedLayer];

  const changeWorkspace = (next: Workspace) => {
    setWorkspace(next);
    setSelectedLayer(0);
    setPlaying(next === "walkthrough");
    setError(null);
  };

  const loadModel = async () => {
    setBusy(true);
    setError(null);
    try {
      const status = await api.loadModel(routeId);
      setModelStatus(status);
      setLiveTrace(null);
    } catch (caught) {
      setError(errorText(caught));
    } finally {
      setBusy(false);
    }
  };

  const infer = async (pixels: number[]) => {
    setBusy(true);
    setError(null);
    try {
      const trace = await api.infer(pixels);
      setLiveTrace(trace);
      setSelectedLayer(0);
      setPlaying(true);
    } catch (caught) {
      setError(errorText(caught));
      throw caught;
    } finally {
      setBusy(false);
    }
  };

  if (contract === null || referenceTrace === null || routes.length === 0) {
    return (
      <EmptyScreen
        message={error ?? "正在校验本地模型、参考轨迹与网络展示契约…"}
      />
    );
  }

  return (
    <div className="app-shell">
      <div className="desktop-warning">
        本产品为桌面学习实验室，请把窗口宽度调整到至少 1100px。
      </div>

      <header className="topbar">
        <button
          className="brand"
          type="button"
          onClick={() => changeWorkspace("walkthrough")}
        >
          <span className="brand-mark">D</span>
          <span>
            <strong>DIGIT // LAB</strong>
            <small>手写数字识别学习实验室</small>
          </span>
        </button>
        <nav aria-label="一级工作区">
          {(
            [
              ["walkthrough", "教学推演"],
              ["routes", "挑战路线"],
              ["live", "真实实验"],
            ] as const
          ).map(([id, label]) => (
            <button
              className={workspace === id ? "is-active" : ""}
              type="button"
              key={id}
              onClick={() => changeWorkspace(id)}
            >
              <span>0{["walkthrough", "routes", "live"].indexOf(id) + 1}</span>
              {label}
            </button>
          ))}
        </nav>
        <div className="runtime-badge">
          <i className={modelStatus.loaded ? "is-ready" : ""} />
          <span>
            LOCAL RUNTIME
            <strong>
              {modelStatus.loaded
                ? `${modelStatus.route?.toUpperCase()} 已加载`
                : "等待模型"}
            </strong>
          </span>
        </div>
      </header>

      {error !== null && (
        <aside className="error-banner" role="alert">
          <strong>当前动作已停止</strong>
          <span>{error}</span>
          <button type="button" onClick={() => setError(null)}>
            关闭
          </button>
        </aside>
      )}

      <main>
        {workspace === "walkthrough" && (
          <>
            <section className="workspace-heading">
              <div>
                <span className="section-index">01 / INSTRUCTIONAL TRACE</span>
                <h1>
                  看见一个数字
                  <br />
                  <em>如何穿过神经网络</em>
                </h1>
              </div>
              <div className="heading-copy">
                <p>
                  这不是模拟动画。下方每一个亮起的单元都来自固定模型对真实
                  MNIST 样例的一次本地推理。
                </p>
                <div className="truth-seal">
                  <i />
                  <span>
                    TRACE SOURCE
                    <strong>PRECOMPUTED · AUTHENTIC</strong>
                  </span>
                </div>
              </div>
            </section>

            <PlaybackControls
              selectedIndex={selectedLayer}
              layerCount={contract.layers.length}
              playing={playing}
              speedIndex={speedIndex}
              onPlayingChange={setPlaying}
              onSelectedIndexChange={setSelectedLayer}
              onSpeedChange={setSpeedIndex}
            />
            <NetworkStage
              contract={contract}
              trace={referenceTrace}
              selectedIndex={selectedLayer}
              onSelect={(index) => {
                setSelectedLayer(index);
                setPlaying(false);
              }}
            />
            <section className="code-section">
              <div className="section-intro">
                <span className="panel-eyebrow">CODE ↔ MODEL</span>
                <h2>动画中的层，就是这份真实代码</h2>
                <p>
                  网页只读展示本地 Python source。绿色行由稳定 layer ID
                  对齐，不按屏幕位置猜测。
                </p>
              </div>
              <CodePane
                files={codeFiles}
                selectedPath={selectedCodePath}
                onSelectPath={setSelectedCodePath}
                activeAnchor={activeLayer?.code_anchor}
              />
            </section>
          </>
        )}

        {workspace === "routes" && (
          <>
            <section className="workspace-heading route-heading">
              <div>
                <span className="section-index">02 / CHALLENGE ROUTES</span>
                <h1>
                  同一个模型，
                  <br />
                  <em>三种动手深度</em>
                </h1>
              </div>
              <div className="heading-copy">
                <p>
                  难度只改变你承担的训练责任。网络结构、最终模型文件和真实实验完全一致。
                </p>
              </div>
            </section>

            <div className="route-card-grid">
              {routes.map((item) => (
                <button
                  className={`route-card ${
                    item.id === routeId ? "is-active" : ""
                  }`}
                  type="button"
                  key={item.id}
                  onClick={() => setRouteId(item.id)}
                >
                  <span className="route-level">LEVEL {item.level}</span>
                  <h2>{item.name}</h2>
                  <small>{item.term}</small>
                  <p>{item.tagline}</p>
                  <span className="route-arrow">选择路线 ↗</span>
                </button>
              ))}
            </div>

            {route !== null && (
              <section className="route-detail">
                <div className="route-brief">
                  <span className="panel-eyebrow">
                    YOUR RESPONSIBILITY · {route.level}
                  </span>
                  <h2>{route.name}</h2>
                  <ol>
                    {route.responsibilities.map((responsibility) => (
                      <li key={responsibility}>{responsibility}</li>
                    ))}
                  </ol>
                  <div className="artifact-callout">
                    <span>固定产物位置</span>
                    <code>{route.model_path}</code>
                  </div>
                  <div className="command-stack">
                    {route.commands.map((command) => (
                      <code key={command}>
                        <span>$</span> {command}
                      </code>
                    ))}
                  </div>
                  <button
                    type="button"
                    className="button button-primary"
                    onClick={() => changeWorkspace("live")}
                  >
                    带这条路线进入真实实验
                  </button>
                </div>
                <CodePane
                  files={codeFiles}
                  selectedPath={selectedCodePath}
                  onSelectPath={setSelectedCodePath}
                />
              </section>
            )}
          </>
        )}

        {workspace === "live" && (
          <>
            <section className="workspace-heading live-heading">
              <div>
                <span className="section-index">03 / LIVE LOCAL INFERENCE</span>
                <h1>
                  现在，换成
                  <br />
                  <em>你本机的模型</em>
                </h1>
              </div>
              <div className="heading-copy">
                <p>
                  选择一条固定路线并显式加载它的 `.pth`。你的笔画、模型和每层
                  tensor 都只在这台电脑上处理。
                </p>
                <div className="truth-seal live">
                  <i />
                  <span>
                    TRACE SOURCE
                    <strong>LIVE · LOCAL · REAL</strong>
                  </span>
                </div>
              </div>
            </section>

            <section className="live-console">
              <div className="model-loader">
                <span className="panel-eyebrow">01 · CHOOSE ARTIFACT</span>
                <h2>加载哪一个模型？</h2>
                <div className="route-switcher">
                  {routes.map((item) => (
                    <button
                      type="button"
                      className={routeId === item.id ? "is-active" : ""}
                      key={item.id}
                      onClick={() => setRouteId(item.id)}
                    >
                      <span>{item.level}</span>
                      {item.name}
                    </button>
                  ))}
                </div>
                {route !== null && (
                  <>
                    <code className="model-path">{route.model_path}</code>
                    <button
                      type="button"
                      className="button button-primary"
                      disabled={busy}
                      onClick={() => void loadModel()}
                    >
                      {busy ? "正在校验…" : "严格校验并加载 state_dict"}
                    </button>
                  </>
                )}
                <div className="model-state">
                  <i className={modelStatus.loaded ? "is-ready" : ""} />
                  {modelStatus.loaded ? (
                    <span>
                      已加载 <strong>{modelStatus.model_path}</strong>
                    </span>
                  ) : (
                    <span>还没有模型进入 runtime</span>
                  )}
                </div>
              </div>

              <div className="draw-station">
                <span className="panel-eyebrow">02 · WRITE A DIGIT</span>
                <h2>写下一个 0–9 的数字</h2>
                <DrawingCanvas
                  samplePixels={referenceTrace.input_pixels}
                  disabled={!modelStatus.loaded || busy}
                  onInfer={infer}
                />
              </div>
            </section>

            {liveTrace !== null ? (
              <>
                <div className="live-result-heading">
                  <div>
                    <span>真实预测</span>
                    <strong>{liveTrace.predicted_digit}</strong>
                  </div>
                  <p>
                    下方已经切换为当前笔画 × 当前已加载模型的实时轨迹。
                    选择任一层检查真实 tensor。
                  </p>
                </div>
                <PlaybackControls
                  selectedIndex={selectedLayer}
                  layerCount={contract.layers.length}
                  playing={playing}
                  speedIndex={speedIndex}
                  onPlayingChange={setPlaying}
                  onSelectedIndexChange={setSelectedLayer}
                  onSpeedChange={setSpeedIndex}
                />
                <NetworkStage
                  contract={contract}
                  trace={liveTrace}
                  selectedIndex={selectedLayer}
                  onSelect={(index) => {
                    setSelectedLayer(index);
                    setPlaying(false);
                  }}
                />
              </>
            ) : (
              <div className="awaiting-trace">
                <span>LIVE TRACE PORT</span>
                <p>加载模型并写下一个数字后，真实内部数据会在这里展开。</p>
              </div>
            )}
          </>
        )}
      </main>

      <footer>
        <span>MNIST · 28×28 · 10 CLASSES</span>
        <span>{contract.architecture_version}</span>
        <span>NO CLOUD · NO TELEMETRY</span>
      </footer>
    </div>
  );
}
