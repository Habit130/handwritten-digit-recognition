import { useEffect, useRef, useState } from "react";

import { prepareMnistPixels } from "../lib/input";

interface DrawingCanvasProps {
  samplePixels: number[];
  disabled: boolean;
  onInfer: (pixels: number[]) => Promise<void>;
}

const CANVAS_SIZE = 280;

export function DrawingCanvas({
  samplePixels,
  disabled,
  onInfer,
}: DrawingCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const drawingRef = useRef(false);
  const lastPointRef = useRef<{ x: number; y: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const clear = () => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");
    if (canvas === null || context === null || context === undefined) return;
    context.fillStyle = "#020604";
    context.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
    setError(null);
  };

  useEffect(() => {
    clear();
  }, []);

  const pointFromEvent = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const bounds = event.currentTarget.getBoundingClientRect();
    return {
      x: ((event.clientX - bounds.left) / bounds.width) * CANVAS_SIZE,
      y: ((event.clientY - bounds.top) / bounds.height) * CANVAS_SIZE,
    };
  };

  const startDrawing = (event: React.PointerEvent<HTMLCanvasElement>) => {
    event.currentTarget.setPointerCapture(event.pointerId);
    drawingRef.current = true;
    lastPointRef.current = pointFromEvent(event);
    setError(null);
  };

  const draw = (event: React.PointerEvent<HTMLCanvasElement>) => {
    if (!drawingRef.current) return;
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");
    const previous = lastPointRef.current;
    if (context === null || context === undefined || previous === null) return;
    const next = pointFromEvent(event);
    context.strokeStyle = "#f4ffe6";
    context.lineWidth = 24;
    context.lineCap = "round";
    context.lineJoin = "round";
    context.beginPath();
    context.moveTo(previous.x, previous.y);
    context.lineTo(next.x, next.y);
    context.stroke();
    lastPointRef.current = next;
  };

  const stopDrawing = () => {
    drawingRef.current = false;
    lastPointRef.current = null;
  };

  const loadSample = () => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");
    if (canvas === null || context === null || context === undefined) return;
    clear();
    const image = context.createImageData(28, 28);
    samplePixels.forEach((value, index) => {
      const channel = Math.round(value * 255);
      const offset = index * 4;
      image.data[offset] = channel;
      image.data[offset + 1] = channel;
      image.data[offset + 2] = channel;
      image.data[offset + 3] = 255;
    });
    const buffer = document.createElement("canvas");
    buffer.width = 28;
    buffer.height = 28;
    const bufferContext = buffer.getContext("2d");
    if (bufferContext === null) throw new Error("Canvas 2D is unavailable");
    bufferContext.putImageData(image, 0, 0);
    context.imageSmoothingEnabled = true;
    context.drawImage(buffer, 0, 0, CANVAS_SIZE, CANVAS_SIZE);
  };

  const infer = async () => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");
    if (canvas === null || context === null || context === undefined) return;
    try {
      const image = context.getImageData(0, 0, CANVAS_SIZE, CANVAS_SIZE);
      const grayscale = new Array<number>(CANVAS_SIZE * CANVAS_SIZE);
      for (let index = 0; index < grayscale.length; index += 1) {
        grayscale[index] = image.data[index * 4] / 255;
      }
      const pixels = prepareMnistPixels(
        grayscale,
        CANVAS_SIZE,
        CANVAS_SIZE,
      );
      setError(null);
      await onInfer(pixels);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    }
  };

  return (
    <div className="drawing-panel">
      <div className="canvas-frame">
        <div className="canvas-axis canvas-axis-x">28 columns</div>
        <canvas
          ref={canvasRef}
          className="drawing-canvas"
          width={CANVAS_SIZE}
          height={CANVAS_SIZE}
          onPointerDown={startDrawing}
          onPointerMove={draw}
          onPointerUp={stopDrawing}
          onPointerCancel={stopDrawing}
          aria-label="用鼠标或触控板书写一个数字"
        />
        <div className="canvas-axis canvas-axis-y">28 rows</div>
      </div>
      <div className="drawing-actions">
        <button className="button button-quiet" type="button" onClick={clear}>
          清空
        </button>
        <button
          className="button button-quiet"
          type="button"
          onClick={loadSample}
        >
          载入样例 7
        </button>
        <button
          className="button button-primary"
          type="button"
          disabled={disabled}
          onClick={() => void infer()}
        >
          整理为 28×28 并识别
        </button>
      </div>
      {error !== null && <p className="inline-error">{error}</p>}
    </div>
  );
}
