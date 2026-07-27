import { describe, expect, it } from "vitest";

import { prepareMnistPixels } from "./input";

describe("prepareMnistPixels", () => {
  it("crops, scales, and centers a handwritten stroke", () => {
    const source = new Array<number>(100 * 100).fill(0);
    for (let y = 20; y < 80; y += 1) {
      for (let x = 68; x < 76; x += 1) {
        source[y * 100 + x] = 1;
      }
    }

    const pixels = prepareMnistPixels(source, 100, 100);
    const mass = pixels.reduce((sum, value) => sum + value, 0);
    const weightedX = pixels.reduce(
      (sum, value, index) => sum + (index % 28) * value,
      0,
    );
    const weightedY = pixels.reduce(
      (sum, value, index) => sum + Math.floor(index / 28) * value,
      0,
    );

    expect(pixels).toHaveLength(784);
    expect(mass).toBeGreaterThan(0);
    expect(Math.abs(weightedX / mass - 13.5)).toBeLessThanOrEqual(0.5);
    expect(Math.abs(weightedY / mass - 13.5)).toBeLessThanOrEqual(0.5);
  });

  it("rejects an empty drawing", () => {
    expect(() =>
      prepareMnistPixels(new Array<number>(100).fill(0), 10, 10),
    ).toThrow("画板还是空的");
  });
});
