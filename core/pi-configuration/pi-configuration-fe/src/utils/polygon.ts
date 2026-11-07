import type { Vector3Dto } from '@/types/homeObject'

type Point = Pick<Vector3Dto, 'x' | 'y'>

const cross = (a: Point, b: Point, c: Point) =>
  (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

const onSegment = (a: Point, b: Point, p: Point) =>
  cross(a, b, p) === 0 &&
  p.x >= Math.min(a.x, b.x) && p.x <= Math.max(a.x, b.x) &&
  p.y >= Math.min(a.y, b.y) && p.y <= Math.max(a.y, b.y)

export function isSimplePolygon(points: Point[]): boolean {
  if (points.some(p => !Number.isFinite(p.x) || !Number.isFinite(p.y))) return false
  for (let i = 0; i < points.length; i++) {
    const a = points[i]!
    const b = points[(i + 1) % points.length]!
    if (points.length < 3) continue
    if (a.x === b.x && a.y === b.y) return false
    const previous = points[(i + points.length - 1) % points.length]!
    if (cross(previous, a, b) === 0 &&
      (previous.x - a.x) * (b.x - a.x) + (previous.y - a.y) * (b.y - a.y) > 0) return false
    for (let j = i + 1; j < points.length; j++) {
      if (j === i + 1 || (i === 0 && j === points.length - 1)) continue
      const c = points[j]!
      const d = points[(j + 1) % points.length]!
      if (onSegment(a, b, c) || onSegment(a, b, d) ||
        onSegment(c, d, a) || onSegment(c, d, b) ||
        (cross(a, b, c) * cross(a, b, d) < 0 &&
          cross(c, d, a) * cross(c, d, b) < 0)) return false
    }
  }
  return true
}

export function pointInPolygon(point: Point, points: Point[]): boolean {
  if (points.length < 3) return false
  let inside = false
  for (let i = 0; i < points.length; i++) {
    const a = points[i]!
    const b = points[(i + 1) % points.length]!
    if (onSegment(a, b, point)) return true
    if ((a.y > point.y) !== (b.y > point.y) &&
      point.x < (b.x - a.x) * (point.y - a.y) / (b.y - a.y) + a.x) inside = !inside
  }
  return inside
}
