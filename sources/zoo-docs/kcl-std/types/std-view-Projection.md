Source URL: https://zoo.dev/docs/kcl-std/types/std-view-Projection
Title: view::Projection

# view::Projection

The camera projection of a named view.

**WARNING:** This type is experimental and may change or be removed.

The camera projection of a named view.

```kcl
type Projection {
  | Orthographic
  | Perspective
}
```




### Variants

| Variant | Description |
|---------|-------------|
| `Orthographic` | An object's projected size is independent of its distance from the camera, and parallel edges remain parallel; the convention of engineering drawings. |
| `Perspective` | Apparent size decreases with distance from the camera, as a physical camera sees; parallel edges converge toward vanishing points. |
