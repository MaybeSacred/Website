import { describe, expect, it } from 'vitest'
import { isSimplePolygon, pointInPolygon } from '../polygon'

const polygon = (coordinates: number[][]) => coordinates.map(([x, y]) => ({ x: x!, y: y! }))

describe('polygon geometry', () => {
  it('accepts convex and concave shapes and rejects crossings, touching and overlapping edges', () => {
    expect(isSimplePolygon(polygon([[0, 0], [10, 0], [10, 10], [0, 10]]))).toBe(true)
    expect(isSimplePolygon(polygon([[0, 0], [10, 0], [5, 5], [10, 10], [0, 10]]))).toBe(true)
    for (const coordinates of [
      [[0, 0], [10, 10], [0, 10], [10, 0]],
      [[0, 0], [10, 0], [5, 0], [5, 10]],
      [[0, 0], [10, 0], [10, 10], [0, 0], [0, 10]],
      [[0, 0], [10, 0], [10, 0], [0, 10]],
    ]) expect(isSimplePolygon(polygon(coordinates))).toBe(false)
    expect(isSimplePolygon(polygon([[0, 0], [Infinity, 0], [0, 10]]))).toBe(false)
  })

  it('includes boundaries and handles concave shapes, reversed winding and negative coordinates', () => {
    const points = polygon([[-10, -10], [10, -10], [0, 0], [10, 10], [-10, 10]])
    for (const shape of [points, [...points].reverse()]) {
      expect(pointInPolygon({ x: -5, y: 0 }, shape)).toBe(true)
      expect(pointInPolygon({ x: 5, y: 0 }, shape)).toBe(false)
      expect(pointInPolygon({ x: -10, y: 0 }, shape)).toBe(true)
      expect(pointInPolygon({ x: 0, y: 0 }, shape)).toBe(true)
      expect(pointInPolygon({ x: 20, y: 0 }, shape)).toBe(false)
    }
    expect(pointInPolygon({ x: 0, y: 0 }, [])).toBe(false)
  })
})
