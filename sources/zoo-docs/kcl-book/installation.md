Source URL: https://zoo.dev/docs/kcl-book/installation.html
Title: Installation

# Installation
There are two main ways to work with KCL. You can use [Zoo Design Studio](https://zoo.dev/modeling-app), our all-in-one application built specifically for KCL designs, or you can use a traditional programming interface with your own text editor. We definitely recommend the Zoo Design Studio.

## Zoo Design Studio
You can download [Zoo Design Studio](https://zoo.dev/modeling-app), then open it and get started. There's a KCL code pane -- click the Code Editor button on the left edge of the screen. That's it! Get ready to design in KCL.

You'll note that when you write KCL code, the live 3D view updates, showing the model you've defined. And if you use the point-and-click buttons (to draw lines, or to select faces for extruding, or edges for filletting), the corresponding lines of code get highlighted. This two-way communication between the code and visuals is the key reason we think KCL will succeed where other code-CAD solutions failed. It's easy to tell exactly what part of the model your code corresponds to.

## Traditional code editing
You can download the [Zoo CLI](https://zoo.dev/docs/cli/manual), which lets you execute KCL programs and download some sort of visualization. You can download your KCL models as 3D files or as 2D images. Use `zoo kcl --help` to learn more.

You can edit KCL in whatever text editor you prefer. If you're using VSCode you can use our [VSCode extension](https://marketplace.visualstudio.com/items?itemName=KittyCAD.kcl-language-server). For all other editors, our [LSP](https://github.com/KittyCAD/modeling-app/tree/main/rust/kcl-language-server) and [Tree-sitter grammar](https://github.com/KittyCAD/tree-sitter-kcl) are available. If you're interested in adding support for other editors or developer tools, please let us know! We're happy to work with you for more open-source KCL support.

## Contributing to KCL
Our [GitHub](https://github.com/KittyCAD/modeling-app) for Zoo Design Studio has all of our developer tooling and the language runtime. Please take a look there if you'd like to open any bugs or contribute to KCL! This book itself is [available on GitHub too](https://github.com/KittyCAD/kcl-book). Feel free to open issues or PRs.
