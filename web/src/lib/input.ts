const TARGET_SIZE = 28;
const DIGIT_SIZE = 20;
const INK_THRESHOLD = 0.04;

export function prepareMnistPixels(
  source: readonly number[],
  width: number,
  height: number,
): number[] {
  if (source.length !== width * height) {
    throw new Error(
      `source contains ${source.length} pixels; expected ${width * height}`,
    );
  }

  let minX = width;
  let minY = height;
  let maxX = -1;
  let maxY = -1;
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      if ((source[y * width + x] ?? 0) > INK_THRESHOLD) {
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x);
        maxY = Math.max(maxY, y);
      }
    }
  }
  if (maxX < minX || maxY < minY) {
    throw new Error("画板还是空的，请先写一个数字。");
  }

  const cropWidth = maxX - minX + 1;
  const cropHeight = maxY - minY + 1;
  const scale = DIGIT_SIZE / Math.max(cropWidth, cropHeight);
  const scaledWidth = Math.max(1, Math.round(cropWidth * scale));
  const scaledHeight = Math.max(1, Math.round(cropHeight * scale));
  const centered = new Array<number>(TARGET_SIZE * TARGET_SIZE).fill(0);
  const startX = Math.floor((TARGET_SIZE - scaledWidth) / 2);
  const startY = Math.floor((TARGET_SIZE - scaledHeight) / 2);

  for (let y = 0; y < scaledHeight; y += 1) {
    for (let x = 0; x < scaledWidth; x += 1) {
      const sourceX = Math.min(
        maxX,
        minX + Math.floor(((x + 0.5) * cropWidth) / scaledWidth),
      );
      const sourceY = Math.min(
        maxY,
        minY + Math.floor(((y + 0.5) * cropHeight) / scaledHeight),
      );
      centered[(startY + y) * TARGET_SIZE + startX + x] =
        source[sourceY * width + sourceX] ?? 0;
    }
  }

  let mass = 0;
  let weightedX = 0;
  let weightedY = 0;
  for (let y = 0; y < TARGET_SIZE; y += 1) {
    for (let x = 0; x < TARGET_SIZE; x += 1) {
      const value = centered[y * TARGET_SIZE + x] ?? 0;
      mass += value;
      weightedX += x * value;
      weightedY += y * value;
    }
  }
  if (mass === 0) {
    throw new Error("画板中的笔画太淡，请重新书写。");
  }

  const shiftX = Math.round(13.5 - weightedX / mass);
  const shiftY = Math.round(13.5 - weightedY / mass);
  const shifted = new Array<number>(TARGET_SIZE * TARGET_SIZE).fill(0);
  for (let y = 0; y < TARGET_SIZE; y += 1) {
    for (let x = 0; x < TARGET_SIZE; x += 1) {
      const targetX = x + shiftX;
      const targetY = y + shiftY;
      if (
        targetX >= 0 &&
        targetX < TARGET_SIZE &&
        targetY >= 0 &&
        targetY < TARGET_SIZE
      ) {
        shifted[targetY * TARGET_SIZE + targetX] =
          centered[y * TARGET_SIZE + x] ?? 0;
      }
    }
  }
  return shifted.map((value) => Math.min(1, Math.max(0, value)));
}
