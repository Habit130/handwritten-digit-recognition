import type {
  LayerContract,
  LayerTrace,
  NetworkContract,
  NetworkTrace,
} from "../lib/types";
import { HeatmapCanvas } from "./HeatmapCanvas";

interface NetworkStageProps {
  contract: NetworkContract;
  trace: NetworkTrace;
  selectedIndex: number;
  onSelect: (index: number) => void;
}

function shapeLabel(shape: number[]): string {
  return shape.slice(1).join(" × ");
}

function LayerNode({
  layer,
  trace,
  index,
  selectedIndex,
  onSelect,
}: {
  layer: LayerContract;
  trace: LayerTrace;
  index: number;
  selectedIndex: number;
  onSelect: (index: number) => void;
}) {
  const state =
    index === selectedIndex
      ? "is-active"
      : index < selectedIndex
        ? "is-passed"
        : "";
  return (
    <button
      className={`layer-node ${state}`}
      type="button"
      onClick={() => onSelect(index)}
      aria-pressed={index === selectedIndex}
    >
      <span className="layer-node-index">
        {String(index + 1).padStart(2, "0")}
      </span>
      <span className="layer-node-name">{layer.name}</span>
      <span className="layer-node-shape">{shapeLabel(trace.shape)}</span>
    </button>
  );
}

export function NetworkStage({
  contract,
  trace,
  selectedIndex,
  onSelect,
}: NetworkStageProps) {
  const layer = contract.layers[selectedIndex];
  const layerTrace = trace.layers[selectedIndex];
  if (layer === undefined || layerTrace === undefined) {
    throw new Error(`Missing layer at index ${selectedIndex}`);
  }

  return (
    <section className="network-stage" aria-label="网络逐层数据舞台">
      <div className="network-rail-wrap">
        <div className="network-rail">
          {contract.layers.map((item, index) => {
            const itemTrace = trace.layers[index];
            if (itemTrace === undefined) {
              throw new Error(`Trace is missing layer ${item.id}`);
            }
            return (
              <LayerNode
                key={item.id}
                layer={item}
                trace={itemTrace}
                index={index}
                selectedIndex={selectedIndex}
                onSelect={onSelect}
              />
            );
          })}
        </div>
      </div>

      <div className="inspection-grid">
        <div className="tensor-visual">
          <div className="panel-eyebrow">
            ACTUAL TENSOR · {layerTrace.values.length.toLocaleString()} VALUES
          </div>
          <HeatmapCanvas
            values={layerTrace.values}
            shape={layerTrace.shape}
            label={layer.name}
          />
          <div className="tensor-scale">
            <span>min {layerTrace.min.toFixed(3)}</span>
            <span>真实中间数据</span>
            <span>max {layerTrace.max.toFixed(3)}</span>
          </div>
        </div>

        <article className="layer-inspector">
          <div className="inspector-number">
            LAYER {String(selectedIndex + 1).padStart(2, "0")}
          </div>
          <h3>{layer.name}</h3>
          <div className="english-term">{layer.term}</div>
          <p>{layer.summary}</p>
          <dl className="layer-facts">
            <div>
              <dt>OPERATION</dt>
              <dd>{layer.operation}</dd>
            </div>
            <div>
              <dt>OUTPUT SHAPE</dt>
              <dd>{layerTrace.shape.join(" × ")}</dd>
            </div>
            <div>
              <dt>CODE ANCHOR</dt>
              <dd>#{layer.code_anchor}</dd>
            </div>
          </dl>
        </article>

        <div className="probability-panel">
          <div className="panel-eyebrow">TEN-CLASS OUTPUT</div>
          <div className="prediction-mark">
            <span>模型判断</span>
            <strong>{trace.predicted_digit}</strong>
          </div>
          <div className="probability-bars">
            {trace.probabilities.map((probability, digit) => (
              <div
                className={`probability-row ${
                  digit === trace.predicted_digit ? "is-winner" : ""
                }`}
                key={digit}
              >
                <span>{digit}</span>
                <div>
                  <i style={{ width: `${probability * 100}%` }} />
                </div>
                <em>{(probability * 100).toFixed(1)}%</em>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
