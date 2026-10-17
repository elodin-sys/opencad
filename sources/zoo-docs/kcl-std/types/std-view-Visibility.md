Source URL: https://zoo.dev/docs/kcl-std/types/std-view-Visibility
Title: view::Visibility

# view::Visibility

Whether the objects of a named view start visible or hidden.

**WARNING:** This type is experimental and may change or be removed.

Whether the objects of a named view start visible or hidden.

```kcl
type Visibility {
  | Show
  | Hide
}
```

This is the view's baseline: it applies to every object, and the view's
`except` list names the objects it does not apply to.


### Variants

| Variant | Description |
|---------|-------------|
| `Show` | Every object is visible, except the ones the view excepts, which are hidden. |
| `Hide` | Every object is hidden, except the ones the view excepts, which are the only visible ones. |
