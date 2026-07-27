import { useEffect, useRef } from "react";

interface HeatmapCanvasProps {
  values: number[];
  shape: number[];
  label: string;
}

function valueColor(value: number, min: number, max: number): string {
  if (value >= 0) {
    const ratio = max > 0 ? Math.min(1, value / max) : 0;
    return `rgba(${Math.round(112 + ratio * 90)}, ${Math.round(
      190 + ratio * 65,
    )}, ${Math.round(170 - ratio * 110)}, ${0.13 + ratio * 0.87})`;
  }
  const ratio = min < 0 ? Math.min(1, value / min) : 0;
  return `rgba(${Math.round(160 + ratio * 95)}, ${Math.round(
    110 - ratio * 45,
  )}, ${Math.round(90 - ratio * 45)}, ${0.13 + ratio * 0.87})`;
}

export function HeatmapCanvas({
  values,
  shape,
  label,
}: HeatmapCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas === null) return;
    const context = canvas.getContext("2d");
    if (context === null) return;

    const size = 360;
    canvas.width = size;
    canvas.height = size;
    context.fillStyle = "#07100e";
    context.fillRect(0, 0, size, size);

    const min = Math.min(...values);
    const max = Math.max(...values);
    const isFeatureMap = shape.length === 4;
    const channels = isFeatureMap ? (shape[1] ?? 1) : 1;
    const mapHeight = isFeatureMap ? (shape[2] ?? 1) : 1;
    const mapWidth = isFeatureMap ? (shape[3] ?? values.length) : values.length;
    const columns = isFeatureMap ? Math.ceil(Math.sqrt(channels)) : 1;
    const rows = isFeatureMap ? Math.ceil(channels / columns) : 1;
    const gap = isFeatureMap ? 6 : 0;
    const tileSize = Math.min(
      (size - gap * (columns + 1)) / columns,
      (size - gap * (rows + 1)) / rows,
    );
    const cellSize = isFeatureMap
      ? Math.max(1, tileSize / Math.max(mapWidth, mapHeight))
      : Math.max(4, Math.min(30, size / Math.ceil(Math.sqrt(values.length))));

    if (isFeatureMap) {
      for (let channel = 0; channel < channels; channel += 1) {
        const tileX = gap + (channel % columns) * (tileSize + gap);
        const tileY = gap + Math.floor(channel / columns) * (tileSize + gap);
        for (let y = 0; y < mapHeight; y += 1) {
          for (let x = 0; x < mapWidth; x += 1) {
            const index =
              channel * mapWidth * mapHeight + y * mapWidth + x;
            context.fillStyle = valueColor(values[index] ?? 0, min, max);
            context.fillRect(
              tileX + x * cellSize,
              tileY + y * cellSize,
              Math.ceil(cellSize),
              Math.ceil(cellSize),
            );
          }
        }
      }
    } else {
      const columnsForVector = Math.ceil(Math.sqrt(values.length));
      const offset =
        (size - columnsForVector * cellSize) / 2;
      values.forEach((value, index) => {
        const x = index % columnsForVector;
        const y = Math.floor(index / columnsForVector);
        context.fillStyle = valueColor(value, min, max);
        context.fillRect(
          offset + x * cellSize,
          offset + y * cellSize,
          Math.ceil(cellSize - 1),
          Math.ceil(cellSize - 1),
        );
      });
    }
  }, [shape, values]);

  return (
    <canvas
      ref={canvasRef}
      className="heatmap-canvas"
      aria-label={`${label} 的真实 tensor 可视化`}
    />
  );
}
